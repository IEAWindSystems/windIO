import pytest
import windIO
import windIO.schemas
import jsonschema.exceptions


def test_windIOMetaSchema():
    windIO.schemas.windIOMetaSchema.check_schema(
        dict(
            title="Dummy test schema",
            properties=dict(
                var1=dict(type="number"),
                var2=dict(type="integer"),
                var3=dict(type="string"),
                var_with_units=dict(type="number", units="m*s"),
                var_none_with_units=dict(type="number", units="dimensionless"),
            ),
            definitions=dict(definitions_can_contain_any_keyword=5),
        )
    )

    with pytest.raises(
        jsonschema.exceptions.ValidationError, match="Additional properties are not allowed"
    ):
        windIO.schemas.windIOMetaSchema.check_schema(
            dict(title="Failed keyword", not_a_key_word=5)
        )

    with pytest.raises(jsonschema.exceptions.ValidationError, match="5 is not of type"):
        windIO.schemas.windIOMetaSchema.check_schema(
            dict(
                title="Units should be a string",
                properties=dict(var_with_units=dict(type="number", units=5)),
            )
        )

    with pytest.raises(
        jsonschema.exceptions.ValidationError, match="'not_a_units' is not a"
    ):
        windIO.schemas.windIOMetaSchema.check_schema(
            dict(
                title="Units should have a number format",
                properties=dict(
                    var_with_units=dict(type="number", units="not_a_units")
                ),
            )
        )

    with pytest.raises(jsonschema.exceptions.ValidationError, match="'None' is not a"):
        windIO.schemas.windIOMetaSchema.check_schema(
            dict(
                title="Units should only be `none`",
                properties=dict(var_with_units=dict(type="number", units="None")),
            )
        )
