
from __future__ import annotations
from ruamel.yaml import YAML
import os
import copy
from pathlib import Path, PosixPath, WindowsPath
import jsonschema
import json
import xarray as xr
from urllib.parse import urljoin

### API design
import windIO.yaml
import windIO.examples.plant
import windIO.examples.turbine
import windIO.schemas

from .examples import plant as plant_ex, turbine as turbine_ex
from windIO.yaml import load_yaml, write_yaml
### API design

def _enforce_no_additional_properties(schema):
    """Recursively set additionalProperties: false for all objects in the schema"""
    if isinstance(schema, dict):

        # If this is an object type schema, and additionalProperties is not specified,
        #   set additionalProperties: false
        if (schema.get('type') == 'object' or 'properties' in schema) and 'additionalProperties' not in schema:
            schema['additionalProperties'] = False
        
        # Recursively process all nested schemas
        for key, value in schema.items():
            if key == 'properties':
                # Process each property's schema
                for prop_schema in value.values():
                    _enforce_no_additional_properties(prop_schema)
            elif key in ['items', 'additionalItems']:
                # Process array item schemas
                _enforce_no_additional_properties(value)
            elif key in ['oneOf', 'anyOf', 'allOf']:
                # Process each subschema in these combining keywords
                for subschema in value:
                    _enforce_no_additional_properties(subschema)
    return schema

def _add_local_schemas_to(resolver, schema_folder, base_uri, schema_ext_lst=['.json', '.yaml', '.yml']):
    '''Function from https://gist.github.com/mrtj/d59812a981da17fbaa67b7de98ac3d4b#file-local_ref-py
    Add local schema instances to a resolver schema cache.

    Args:
        resolver (jsonschema.RefResolver): the reference resolver
        schema_folder (str): the local folder of the schemas.
        base_uri (str): the base URL that you actually use in your '$id' tags
            in the schemas
        schema_ext (str): filter files with this extension in the schema_folder
    '''
    for dir, _, files in os.walk(schema_folder):
        for file in files:
            if Path(file).suffix in schema_ext_lst:
                schema_path = Path(dir) / Path(file)
                rel_path = schema_path.relative_to(schema_folder)
                try:
                    with open(schema_path) as schema_file:
                        if schema_path.suffix == '.json':
                            schema_doc = json.load(schema_file)
                        if schema_path.suffix in ['.yml', '.yaml']:
                            schema_doc = load_yaml(schema_file)

                    key = urljoin(base_uri, str(rel_path))
                    resolver.store[key] = schema_doc
                # except (ScannerError, ParserError):
                except Exception as err:
                    print(f"Reading {file} failed\nWith error:\n{err}")

def validate(input: dict | str | Path, schema_type: str, restrictive: bool = True) -> None:
    """
    Validates a given windIO input based on the selected schema type.

    Args:
        input (dict | str | Path): Input data or path to file to be validated.
        schema_type (str): Type of schema to be used for validation. This must map to one
            of the schema files available in the ``schemas/plant`` or ``schemas/turbine`` folders.
            Examples of valid schema types are 'plant/wind_energy_system' or
            '`turbine/IEAontology_schema`'.
        restrictive (bool, optional): If True, the schema will be modified to enforce
            that no additional properties are allowed. Defaults to True.

    Raises:
        FileNotFoundError: If the schema type is not found in the schemas folder.
        TypeError: If the input type is not supported.
        jsonschema.exceptions.ValidationError: If the input data fails validation
            against the schema.
        jsonschema.exceptions.SchemaError: if the schema itself is invalid.
    
    Returns:
        None
    """
    schema_file = Path(windIO.schemas.__file__).parent / f"{schema_type}.yaml"
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

    base_uri = 'https://www.example.com/schemas/'
    resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)
    schema_folder = Path(schema_file).parent
    _add_local_schemas_to(resolver, schema_folder, base_uri)
    jsonschema.validate(data, schema, resolver=resolver)


def dict_to_netcdf(data_dict, output_filename=None):
    """
    Convert a dictionary (from ds2yml) back to an xarray Dataset and optionally to netCDF file.
    This function infers coordinate dimensions based on array size.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary produced by ds2yml containing coordinates and data variables
    output_filename : str, optional
        Path to save the netCDF file, if None, only the xarray Dataset is returned
        
    Returns:
    --------
    ds : xarray.Dataset
        The reconstructed xarray Dataset
    """
    # Separate coordinates from data variables
    coords = {}
    data_vars = {}
    
    for key, value in data_dict.items():
        # If value is a dictionary with 'dims' and 'data', it's a data variable
        if isinstance(value, dict) and 'dims' in value and 'data' in value:
            data_vars[key] = value
        else:
            # Otherwise, assume it's a coordinate
            coords[key] = value
    
    # Create xarray coordinates - infer dimensions from array shapes
    xr_coords = {}
    for name, values in coords.items():
        # Check if the values are array-like
        if hasattr(values, '__len__') and not isinstance(values, (str, dict)):
            # For array-like coordinates, use the coordinate name as dimension
            xr_coords[name] = xr.DataArray(values, dims=[name])
        else:
            # For scalar coordinates, no dimension needed
            xr_coords[name] = values
    
    # Create xarray data variables
    xr_data_vars = {}
    for name, var_info in data_vars.items():
        # Check if dims are provided and valid
        if 'dims' in var_info and isinstance(var_info['dims'], (list, tuple)):
            dims = var_info['dims']
        else:
            # Fallback: Create generic dimension names based on array shape
            data_shape = np.asarray(var_info['data']).shape
            dims = [f'dim_{i}' for i in range(len(data_shape))]
        
        # Create data array with appropriate dimensions
        xr_data_vars[name] = xr.DataArray(
            data=var_info['data'],
            dims=dims,
            attrs=var_info.get('attrs', {})
        )
    
    # Create dataset
    ds = xr.Dataset(data_vars=xr_data_vars, coords=xr_coords)
    
    # Write to netCDF if output_filename is provided
    if output_filename:
        ds.to_netcdf(output_filename)
    
    return ds

