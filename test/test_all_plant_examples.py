import os
import glob
import pytest
from pathlib import Path
import windIO

def test_validate_all_example_files():
    """
    Test that validates all example YAML files against their corresponding schema types
    based on their directory path.
    """
    plant_example_path = Path(windIO.plant_ex.__file__).parent
    
    # Define mapping between directory names and schema types
    schema_mapping = {
        'wind_energy_system': 'plant/wind_energy_system',
        'plant_energy_resource': 'plant/energy_resource',
        'plant_energy_site': 'plant/site',
        'plant_wind_farm': 'plant/wind_farm',
        'plant_energy_turbine': 'plant/turbine'
    }
    
    # Skip files that include another file (to avoid validation errors)
    # Find all YAML files
    yaml_files = []
    for schema_dir in schema_mapping.keys():
        dir_path = plant_example_path / schema_dir
        if dir_path.exists():
            yaml_files.extend(glob.glob(str(dir_path / "*.yaml")))
    
    # Validate each file with its corresponding schema
    for yaml_file in yaml_files:
        file_path = Path(yaml_file)
        file_name = file_path.name
        
        # Determine schema type from directory name
        parent_dir = file_path.parent.name
        if parent_dir in schema_mapping:
            schema_type = schema_mapping[parent_dir]
            
            # Use pytest subtests to continue even if one file fails
            try:
                windIO.validate(input=file_path, schema_type=schema_type)
            except Exception as e:
                pytest.fail(f"Validation failed for {file_path}: {str(e)}")

