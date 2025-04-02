from pathlib import Path

import jsonschema
import pytest
from jsonschema.exceptions import ValidationError

import windIO

from .conftest import SampleInputs


def test_wind_farm_input(subtests):
    """
    Test a complete wind_farm set of inputs, and ensure that
    optional properties can be excluded.
    """
    with subtests.test("with valid config"):
        config = SampleInputs().wind_farm
        windIO.validate(config, "plant/wind_farm")

    with subtests.test("remove optional electrical_substations"):
        config = SampleInputs().wind_farm
        del config["electrical_substations"]
        windIO.validate(config, "plant/wind_farm")

    with subtests.test("remove optional electrical_collection_array"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]
        windIO.validate(config, "plant/wind_farm")


@pytest.mark.skip(reason="wind farm turbine has optional: true")
def test_wind_farm_invalid_inputs_turbines(subtests):
    """
    Test missing inputs for the wind_farm turbines property.
    """
    with subtests.test("missing turbines"):
        config = SampleInputs().wind_farm
        del config["turbines"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")


def test_wind_farm_invalid_inputs_electrical_substations(subtests):
    """
    Test missing inputs for the wind_farm electrical_substation property.
    """
    with subtests.test("missing electrical_substation"):
        config = SampleInputs().wind_farm
        del config["electrical_substations"][0]["electrical_substation"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")

    with subtests.test("missing electrical_substation coordinates"):
        config = SampleInputs().wind_farm
        del config["electrical_substations"][0]["electrical_substation"]["coordinates"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")

    with subtests.test("remove optional electrical_substation capacity"):
        config = SampleInputs().wind_farm
        del config["electrical_substations"][0]["electrical_substation"]["capacity"]
        windIO.validate(config, "plant/wind_farm") is None


def test_wind_farm_invalid_inputs_electrical_collection_array(subtests):
    """
    Test missing inputs for the wind_farm electrical_collection_array property.
    """
    with subtests.test("missing electrical_collection_array edges"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["edges"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")

    with subtests.test("missing electrical_collection_array cables"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")

    with subtests.test("missing electrical_collection_array cables cable_type"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]["cable_type"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")

    with subtests.test("missing electrical_collection_array cables cross_section"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]["cross_section"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")

    with subtests.test("missing electrical_collection_array cables capacity"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]["capacity"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")

    with subtests.test("missing electrical_collection_array cables cost"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]["cost"]
        with pytest.raises(ValidationError):
            windIO.validate(config, "plant/wind_farm")


def test_plant_valid_schema():
    schema_base = Path(__file__).parent.parent.parent / "windIO" / "schemas" / "plant"
    for fschema in schema_base.rglob("*.yaml"):

        path2schema = schema_base / fschema

        schema = windIO.load_yaml(path2schema)

        base_uri = "https://www.example.com/schemas/"
        resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)
        schema_folder = Path(path2schema).parent
        windIO._add_local_schemas_to(resolver, schema_folder, base_uri)
        windIO.schemas.windIOMetaSchema.resolver = resolver
        windIO.schemas.windIOMetaSchema.check_schema(schema)
