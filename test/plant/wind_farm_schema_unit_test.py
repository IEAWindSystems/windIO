import numpy as np
import numpy.testing as npt
import pytest
from windIO.utils.yml_utils import load_yaml, validate_yaml
from windIO.utils import plant_examples_data_path, plant_schemas_path
from test.plant.conftest import SampleInputs
from jsonschema.exceptions import ValidationError


def test_wind_farm_input(subtests):
    """
    Test a complete wind_farm set of inputs, and ensure that
    optional properties can be excluded.
    """
    with subtests.test("with valid config"):
        config = SampleInputs().wind_farm
        assert validate_yaml(config, plant_schemas_path + "wind_farm.yaml") is None

    with subtests.test("remove optional electrical_substations"):
        config = SampleInputs().wind_farm
        del config["electrical_substations"]
        assert validate_yaml(config, plant_schemas_path + "wind_farm.yaml") is None

    with subtests.test("remove optional electrical_collection_array"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]
        assert validate_yaml(config, plant_schemas_path + "wind_farm.yaml") is None


def test_wind_farm_invalid_inputs_layouts(subtests):
    """
    Test missing inputs for the wind_farm layouts property.
    """
    with subtests.test("missing layouts"):
        config = SampleInputs().wind_farm
        del config["layouts"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")

    with subtests.test("missing layouts initial_layout"):
        config = SampleInputs().wind_farm
        del config["layouts"]["initial_layout"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")

    with subtests.test("missing layouts initial_layout coordinates"):
        config = SampleInputs().wind_farm
        del config["layouts"]["initial_layout"]["coordinates"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")


def test_wind_farm_invalid_inputs_turbines(subtests):
    """
    Test missing inputs for the wind_farm turbines property.
    """
    with subtests.test("missing turbines"):
        config = SampleInputs().wind_farm
        del config["turbines"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")


def test_wind_farm_invalid_inputs_electrical_substations(subtests):
    """
    Test missing inputs for the wind_farm electrical_substation property.
    """
    with subtests.test("missing electrical_substation"):
        config = SampleInputs().wind_farm
        del config["electrical_substations"][0]["electrical_substation"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")

    with subtests.test("missing electrical_substation coordinates"):
        config = SampleInputs().wind_farm
        del config["electrical_substations"][0]["electrical_substation"]["coordinates"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")

    with subtests.test("remove optional electrical_substation capacity"):
        config = SampleInputs().wind_farm
        del config["electrical_substations"][0]["electrical_substation"]["capacity"]
        assert validate_yaml(config, plant_schemas_path + "wind_farm.yaml") is None

def test_wind_farm_invalid_inputs_electrical_collection_array(subtests):
    """
    Test missing inputs for the wind_farm electrical_collection_array property.
    """
    with subtests.test("missing electrical_collection_array edges"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["edges"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")

    with subtests.test("missing electrical_collection_array cables"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")

    with subtests.test("missing electrical_collection_array cables cable_type"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]["cable_type"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")
    
    with subtests.test("missing electrical_collection_array cables cross_section"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]["cross_section"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")
    
    with subtests.test("missing electrical_collection_array cables capacity"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]["capacity"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")
    
    with subtests.test("missing electrical_collection_array cables cost"):
        config = SampleInputs().wind_farm
        del config["electrical_collection_array"]["cables"]["cost"]
        with pytest.raises(ValidationError):
            validate_yaml(config, plant_schemas_path + "wind_farm.yaml")
