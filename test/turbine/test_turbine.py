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

        windIO.schemas.windIOMetaSchema.check_schema(schema)
