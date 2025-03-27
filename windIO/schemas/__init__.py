import jsonschema
try:
    import pint
    has_pint = True
except ImportError:
    has_pint = False

# Extension of the draft 7 schema
windIOMetaSchema = jsonschema.validators.extend(jsonschema.Draft7Validator)

# Extending the meta-schema to include units with `format:"units"`
windIOMetaSchema.META_SCHEMA["title"] = "windIO Meta Schema - an extension of the draft 7 meta schema"
windIOMetaSchema.META_SCHEMA["additionalProperties"] = False
windIOMetaSchema.META_SCHEMA["properties"]["definitions"]["additionalProperties"] = True
windIOMetaSchema.META_SCHEMA["properties"]["units"] = dict(type="string", format="units")
windIOMetaSchema.META_SCHEMA["properties"]["optional"] = windIOMetaSchema.META_SCHEMA["properties"]["required"] # Allow optional

if has_pint:
    # Adding custom "units" format checker
    windIOMetaSchema.units_reg = pint.UnitRegistry()
    windIOMetaSchema.units_reg.define('USD = currency')
    format_checker = windIOMetaSchema.FORMAT_CHECKER
    @format_checker.checks("units", pint.errors.UndefinedUnitError)
    def check_units(instance: object):
        windIOMetaSchema.units_reg.parse_expression(instance)
        return True