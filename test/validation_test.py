from pathlib import Path

import jsonschema.exceptions
import pytest

import windIO


def test_validate_raise():
    # Test the validation error message that is raised and that it provides a useful inside into
    turbine_reference_path = Path(windIO.turbine_ex.__file__).parent

    IEA_15MW_turb_mod = windIO.load_yaml(turbine_reference_path / "IEA-15-240-RWT.yaml")

    # Not a defined entry with strict
    IEA_15MW_turb_mod["components"]["blade"]["reference_axis"]["I_should_not_be_here"] = "Sorry"
    IEA_15MW_turb_mod["components"]["blade"]["outer_shape"]["airfoils"][0]["name"] = 5
    IEA_15MW_turb_mod["materials"][0].pop("name")

    with pytest.raises(jsonschema.exceptions.ValidationError, match="The validation found 3 error"):
        windIO.validate(IEA_15MW_turb_mod, "turbine/turbine_schema")

def test_defaults():
    # Setup the turbine reference path
    turbine_reference_path = Path(windIO.turbine_ex.__file__).parent

    # Load the turbine YAML file
    IEA_15MW_turb_mod = windIO.load_yaml(turbine_reference_path / "IEA-15-240-RWT.yaml")

    # Remove the "number_of_blades" key
    IEA_15MW_turb_mod["assembly"].pop("number_of_blades")

    # Validate the turbine model
    IEA_15MW_turb_nodefaults = windIO.validate(IEA_15MW_turb_mod, "turbine/turbine_schema")

    # Assert that accessing "number_of_blades" raises a KeyError
    with pytest.raises(KeyError, match="'number_of_blades'"):
        _ = IEA_15MW_turb_nodefaults["assembly"]["number_of_blades"]

    # Now let the schema populate the missing keys with default values
    IEA_15MW_turb_defaults = windIO.validate(IEA_15MW_turb_mod, "turbine/turbine_schema", defaults=True)
    _ = IEA_15MW_turb_defaults["assembly"]["number_of_blades"]

def test_validation_IEA_case_studies_1_2():

    plant_reference_path = Path(windIO.plant_ex.__file__).parent
    windIO.validate(
        input=plant_reference_path
        / "wind_energy_system/IEA37_case_study_1_2_wind_energy_system.yaml",
        schema_type="plant/wind_energy_system",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_resource/IEA37_case_study_1_2_energy_resource.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_site/IEA37_case_study_1_2_energy_site.yaml",
        schema_type="plant/site",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_wind_farm/IEA37_case_study_1_2_wind_farm.yaml",
        schema_type="plant/wind_farm",
    )


def test_validation_IEA_case_studies_3():

    plant_reference_path = Path(windIO.plant_ex.__file__).parent

    windIO.validate(
        input=plant_reference_path
        / "wind_energy_system/IEA37_case_study_3_wind_energy_system.yaml",
        schema_type="plant/wind_energy_system",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_resource/IEA37_case_study_3_energy_resource.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_site/IEA37_case_study_3_energy_site.yaml",
        schema_type="plant/site",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_wind_farm/IEA37_case_study_3_wind_farm.yaml",
        schema_type="plant/wind_farm",
    )


def test_validation_IEA_case_studies_4():

    plant_reference_path = Path(windIO.plant_ex.__file__).parent

    windIO.validate(
        input=plant_reference_path
        / "wind_energy_system/IEA37_case_study_4_wind_energy_system.yaml",
        schema_type="plant/wind_energy_system",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_resource/IEA37_case_study_4_energy_resource.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_site/IEA37_case_study_4_energy_site.yaml",
        schema_type="plant/site",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_wind_farm/IEA37_case_study_4_wind_farm.yaml",
        schema_type="plant/wind_farm",
    )


def test_validation_IEA_turbines():

    plant_reference_path = Path(windIO.plant_ex.__file__).parent

    windIO.validate(
        input=plant_reference_path / "plant_energy_turbine/IEA37_3.35MW_turbine.yaml",
        schema_type="plant/turbine",
    )

    windIO.validate(
        input=plant_reference_path / "plant_energy_turbine/IEA37_10MW_turbine.yaml",
        schema_type="plant/turbine",
    )

    windIO.validate(
        input=plant_reference_path / "plant_energy_turbine/IEA37_15MW_turbine.yaml",
        schema_type="plant/turbine",
    )


def test_validation_energy_resources():

    plant_reference_path = Path(windIO.plant_ex.__file__).parent

    # Uniform Resource
    windIO.validate(
        input=plant_reference_path / "plant_energy_resource/UniformResource.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path / "plant_energy_resource/UniformResource_nc.yaml",
        schema_type="plant/energy_resource",
    )

    # UniformWeibull Resource
    windIO.validate(
        input=plant_reference_path
        / "plant_energy_resource/UniformWeibullResource.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_resource/UniformWeibullResource_nc.yaml",
        schema_type="plant/energy_resource",
    )

    # WT distributed Resource
    windIO.validate(
        input=plant_reference_path / "plant_energy_resource/WTResource.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path / "plant_energy_resource/WTResource_nc.yaml",
        schema_type="plant/energy_resource",
    )

    # Gridded Resource
    windIO.validate(
        input=plant_reference_path / "plant_energy_resource/GriddedResource.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path / "plant_energy_resource/GriddedResource_nc.yaml",
        schema_type="plant/energy_resource",
    )


def test_validation_timeseries():

    plant_reference_path = Path(windIO.plant_ex.__file__).parent

    windIO.validate(
        input=plant_reference_path / "plant_energy_resource/timeseries.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_resource/timeseries_with_netcdf.yaml",
        schema_type="plant/energy_resource",
    )

    windIO.validate(
        input=plant_reference_path
        / "plant_energy_resource/timeseries_vertical_variation.yaml",
        schema_type="plant/energy_resource",
    )

if __name__ == "__main__":
    test_validate_raise()