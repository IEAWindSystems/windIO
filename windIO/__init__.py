
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
from .validator import validate

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
