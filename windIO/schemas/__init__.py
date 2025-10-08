"""windIO Meta-schema. A schema used to validate the schemas used in windIO (not used by the average user of windIO)

The windIO Meta-schema extends the JSON-Schema Draft 7: https://json-schema.org/draft-07

It extends the Draft 7 meta-schema in the following ways:

    - Sets `additionalProperties = False`.
      It means that the schema do not allow entries that are not defined by the schema to avoid and catch typos.
    - Adds a `units` field.
      It enables the possibility to add units for ex. `number` entries. The `units` is added with the `format=units`
      which is not defined in the standard format entries: https://json-schema.org/draft/2020-12/draft-bhutton-json-schema-validation-00#rfc.section.7.3
    - Adding an `optional` entry.
      It is a "copy" of the `required` entry which allows to just specify the entries
      that are optional - which is the default if not in the `required` list.

Besides the extension of the Draft 7 Meta-Schema the Python `jsonschema.validator` is also extended:

    - Validation of the `units` format.
      As stated above, the `"format": "units"` is a non-standard format for JSON-schema.
      Therefore the validator is extended with a format validation which is done with the `pint` module:https://pint.readthedocs.io/en/stable/
      It is a light weight pure-python module which enables working with units in Python.
      The validation is simply done my checking if `pint` can parse the units instance.
      The format of the units field is therefore consistent across the schema.
      The default units defined can be seen here: https://github.com/hgrecco/pint/blob/master/pint/default_en.txt
      `pint` is not a required dependency as an average user as they are not expected to validate the windIO schemas them self (but only instances of the schema).
"""

import jsonschema
from pathlib import Path
import jsonschema.validators
import jsonschema.exceptions

try:
    # Checks if `pint` is installed - if not the `units` format is not validated for windIO meta schemas (not relevant for the average user)
    import pint

    has_pint = True
except ImportError:
    has_pint = False

schemaPath = Path(__file__).parent

# Initializing a Draft 7 validator copy
windIOMetaSchema = jsonschema.validators.extend(jsonschema.Draft7Validator)

# Updating the Meta-Schema
windIOMetaSchema.META_SCHEMA["title"] = (
    "windIO Meta Schema - an extension of the draft 7 meta schema"
)
windIOMetaSchema.META_SCHEMA["$id"] = "windIO/schema/meta-schema"
windIOMetaSchema.META_SCHEMA["additionalProperties"] = False
windIOMetaSchema.META_SCHEMA["properties"]["definitions"]["additionalProperties"] = True
windIOMetaSchema.META_SCHEMA["properties"]["units"] = dict(
    type="string", format="units"
)
windIOMetaSchema.META_SCHEMA["properties"]["optional"] = windIOMetaSchema.META_SCHEMA[
    "properties"
][
    "required"
]  # Allow optional


def schema_validation_error_formatter(errs: jsonschema.Draft7Validator.iter_errors, schema_id: str):
    """Formatting validation errors from `.iter_errors` of a jsonschema.validator

    Parameters
    ----------
    errs : jsonschema.Draft7Validator.iter_errors
        iterator with the errors from the validation
    schema_id : str
        Name or ID for the schema used for the validation

    Raises
    ------
    jsonschema.exceptions.ValidationError
        Raised if `errs` is not empty.
    """    
    err_message = ""
    n_errs = 0
    for err in errs:
        n_errs += 1
        _message = f'Error {n_errs}: Failed at instance path `{err.json_path}` with error message: "{err.message}"\n'
        err_message += _message

    if n_errs > 0:
        err_message = (
            f"Validation of schema instance failed for schema `{schema_id}`\nThe validation found {n_errs} error(s) which are further detailed below.\n\n"
            + err_message
        )
        raise jsonschema.exceptions.ValidationError(err_message)


def check_schema(cls, schema, format_checker=jsonschema.validators._UNSET):
    """Modified version of the check_schema for the default Draft7 validator which prints errors using `windIO.schema.schema_validation_error_formatter`"""
    Validator = jsonschema.validators.validator_for(cls.META_SCHEMA, default=cls)
    if format_checker is jsonschema.validators._UNSET:
        format_checker = Validator.FORMAT_CHECKER
    validator = Validator(
        schema=cls.META_SCHEMA,
        format_checker=format_checker,
    )
    schema_validation_error_formatter(
        validator.iter_errors(schema), validator.schema["$id"]
    )


windIOMetaSchema.check_schema = classmethod(check_schema)

if has_pint:
    # Adding a "units" format validator
    # Adding a `pint.UnitRegistry` instance to the validator
    windIOMetaSchema.units_reg = pint.UnitRegistry()
    # Adding non-default units
    windIOMetaSchema.units_reg.define("USD = currency")  # Using USD as the currency
    # Get the validator format-checker
    format_checker = windIOMetaSchema.FORMAT_CHECKER

    # Adding the `units` format checker method: https://python-jsonschema.readthedocs.io/en/stable/api/#jsonschema.FormatChecker.checks
    @format_checker.checks("units", Exception)
    def check_units(instance: object):
        """units format validator. Tests if the `pint` unit-registry can parse the units format"""
        windIOMetaSchema.units_reg.parse_expression(instance)
        return True
