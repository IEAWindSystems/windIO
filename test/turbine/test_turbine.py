import unittest
from pathlib import Path
import windIO
from windIO.converters.windIO2windIO import v1p0_to_v2p0

from jsonschema import Draft7Validator

turbine_reference_path = Path(windIO.turbine_ex.__file__).parent
test_dir = Path(__file__).parent

class TestRegression(unittest.TestCase):
    
    def test_load_IEA_15_240_RWT(self):

        
        path2yaml = turbine_reference_path / "IEA-15-240-RWT.yaml"

        # Verify the file loads
        windIO.load_yaml(path2yaml)

    
    def test_validate_IEA_15_240_RWT(self):

        path2yaml = turbine_reference_path / "IEA-15-240-RWT.yaml"

        # Validate the file
        windIO.validate(path2yaml, schema_type="turbine/turbine_schema")
    
    def test_load_IEA_15_240_RWT_VolturnUS_S(self):

        path2yaml = turbine_reference_path / "IEA-15-240-RWT_VolturnUS-S.yaml"

        # Verify the file loads
        windIO.load_yaml(path2yaml)

    
    def test_validate_IEA_15_240_RWT_VolturnUS_S(self):

        path2yaml = turbine_reference_path / "IEA-15-240-RWT_VolturnUS-S.yaml"

        # Validate the file
        windIO.validate(path2yaml, schema_type="turbine/turbine_schema")

   
    def test_v1p0_2p0_converter_IEA_15_240_RWT(self):
        
        filename_v1p0 = test_dir / "v1p0" / "IEA-15-240-RWT.yaml"
        filename_v2p0 = test_dir / "IEA-15-240-RWT.yaml"
                 
        converter = v1p0_to_v2p0(filename_v1p0, filename_v2p0)
        converter.convert()

        # Now validate the output
        windIO.validate(filename_v2p0, schema_type="turbine/turbine_schema")
    
    def test_v1p0_2p0_converter_IEA_15_240_RWT_VolturnUS_S(self):
        
        filename_v1p0 = test_dir / "v1p0" / "IEA-15-240-RWT_VolturnUS-S.yaml"
        filename_v2p0 = test_dir / "IEA-15-240-RWT_VolturnUS-S.yaml"
                 
        converter = v1p0_to_v2p0(filename_v1p0, filename_v2p0)
        converter.convert()
              
    def test_valid_schema(self):
        
        path2schema = Path(__file__).parent.parent.parent / "windIO" / "schemas" / "turbine" / "turbine_schema.yaml"
        
        schema = windIO.load_yaml(path2schema)

        Draft7Validator.META_SCHEMA["additionalProperties"] = False
        Draft7Validator.META_SCHEMA["properties"]["definitions"]["additionalProperties"] = True
        Draft7Validator.META_SCHEMA["properties"]["units"] = dict(type="string")
        Draft7Validator.META_SCHEMA["properties"]["optional"] = Draft7Validator.META_SCHEMA["properties"]["required"]

        Draft7Validator.check_schema(schema)

        def recursive_require_optional_in_properties(schema, name_list=None):
            if name_list is None:
                name_list = []
            for name in schema.get("required", []):
                assert name in schema["properties"], f"Required property: '{name}' is not in `properties` for {name_list}"
            for name in schema.get("optional", []):
                assert name in schema["properties"], f"Optional property: '{name}' is not in `properties` for {name_list}"
            for name, val in schema.items():
                if name in ["if", "then", "else"]:
                    continue
                if isinstance(val, dict):
                    recursive_require_optional_in_properties(val, name_list+[name])
                if isinstance(val, list):
                    for iel, el in enumerate(val):
                        if isinstance(el, dict):
                            recursive_require_optional_in_properties(el, name_list+[name, iel])
                            
        recursive_require_optional_in_properties(schema)
