from __future__ import annotations

from pathlib import Path, PosixPath, WindowsPath
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource
import copy
import jsonschema
import jsonschema.validators

from .yaml import load_yaml
from .schemas import schemaPath, schema_validation_error_formatter


def retrieve_yaml(uri: str):
    if not uri.endswith(".yaml"):
        raise NoSuchResource(ref=uri)
    uri = uri.removeprefix("windIO/")
    path = schemaPath / Path(uri)
    contents = load_yaml(path)
    return Resource.from_contents(contents)


registry = Registry(retrieve=retrieve_yaml)


def _enforce_no_additional_properties(schema):
    """Recursively set additionalProperties: false for all objects in the schema"""
    if isinstance(schema, dict):

        # If this is an object type schema, and additionalProperties is not specified,
        #   set additionalProperties: false
        if (
            schema.get("type") == "object" or "properties" in schema
        ) and "additionalProperties" not in schema:
            schema["additionalProperties"] = False

        # Recursively process all nested schemas
        for key, value in schema.items():
            if key == "properties":
                # Process each property's schema
                for prop_schema in value.values():
                    _enforce_no_additional_properties(prop_schema)
            elif key in ["items", "additionalItems"]:
                # Process array item schemas
                _enforce_no_additional_properties(value)
            elif key in ["oneOf", "anyOf", "allOf"]:
                # Process each subschema in these combining keywords
                for subschema in value:
                    _enforce_no_additional_properties(subschema)
    return schema


def validate(
    input: dict | str | Path, schema_type: str, restrictive: bool = True, defaults: bool = False,
) -> None:
    """
    Validates a given windIO input based on the selected schema type.

    Args:
        input (dict | str | Path): Input data as a dictionary or a path to a YAML file 
            containing the data to be validated.
        schema_type (str): Type of schema to be used for validation. This must correspond 
            to one of the schema files available in the ``schemas/plant`` or ``schemas/turbine`` 
            folders. Examples of valid schema types include 'plant/wind_energy_system' or 
            'turbine/turbine_schema'.
        restrictive (bool, optional): If True, the schema will be modified to enforce
            that no additional properties are allowed. Defaults to True.
        defaults (bool, optional): If True, default values specified in the schema will 
            be applied to the input data during validation. Defaults to False.

    Raises:
        FileNotFoundError: If the schema file corresponding to the schema type is not found.
        TypeError: If the input type is not supported (must be dict, str, or Path-like).
        jsonschema.exceptions.ValidationError: If the input data fails validation
            against the schema.
        jsonschema.exceptions.SchemaError: If the schema itself is invalid.

    Returns:
        dict: The validated input data. If `defaults` is True, the returned data will 
        include default values specified in the schema.
    """
    schema_file = schemaPath / f"{schema_type}.yaml"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file {schema_file} not found.")

    if type(input) is dict:
        data = copy.deepcopy(input)
    elif type(input) in [str, Path, PosixPath, WindowsPath]:
        data = load_yaml(input)
    else:
        raise TypeError(f"Input type {type(input)} is not supported.")

    schema = load_yaml(schema_file)
    if restrictive:
        schema = _enforce_no_additional_properties(schema)

    if defaults:
        _jsonschema_validate_modified(data, schema, cls = DefaultValidatingDraft7Validator, registry=registry)
    else:
        _jsonschema_validate_modified(data, schema, registry=registry)

    return data


# See: https://python-jsonschema.readthedocs.io/en/stable/faq/#why-doesn-t-my-schema-s-default-property-set-the-default-on-my-instance
def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.items():
            if "default" in subschema:
                instance.setdefault(property, subschema["default"])

        for error in validate_properties(validator, properties, instance, schema):
            yield error

    return jsonschema.validators.extend(validator_class, {"properties": set_defaults})

DefaultValidatingDraft7Validator = extend_with_default(jsonschema.Draft7Validator)

def _jsonschema_validate_modified(instance, schema, cls=None, *args, **kwargs):
    """Modification of the `jsonschema.validate` which is though to provide a better error message when validation fails"""
    if cls is None:
        cls = jsonschema.validators.validator_for(schema)

    cls.check_schema(schema)
    validator = cls(schema, *args, **kwargs)
    schema_validation_error_formatter(validator.iter_errors(instance), schema['$id'])