from __future__ import annotations

import os
from typing import Any
from pathlib import Path

import numpy as np
from ruamel.yaml import YAML
from ruamel.yaml.constructor import SafeConstructor
import xarray as xr
from functools import reduce
import operator
import copy


def fmt(v: Any) -> dict | list | str | float | int:
    """
    Formats a dictionary appropriately for yaml.load by converting Tuples to Lists.

    Args:
        v (Any): Initially, a dictionary of inputs to format. Then, individual
            values within the dictionary.
    """
    if isinstance(v, dict):
        return {k: fmt(v) for k, v in v.items() if fmt(v) != {}}
    elif isinstance(v, tuple):
        return list(v)
    else:
        return v


def ds2yml(ds: xr.Dataset) -> dict:
    """
    Converts the input xr.Dataset to a format compatible with yaml.load.

    Args:
        ds (xr.Dataset): NetCDF data loaded as a xr.Dataset
    """
    d = ds.to_dict()
    return fmt(
        {
            **{k: v["data"] for k, v in d["coords"].items()},
            **d["data_vars"],
        }
    )


def get_YAML(
    typ: str = "safe",
    write_numpy: bool = True,
    read_numpy: bool = False,
    read_include: bool = True,
    n_list_flow_style: int = 1,
) -> YAML:
    """Get `ruamel.yaml.YAML` instance default setting for windIO

    Args:
        typ (str, optional): ruamel.yaml.YAML `typ`. Defaults to "safe".
        write_numpy (bool, optional): Flag for enabling the YAML parser to write numpy types. Defaults to True.
        read_numpy (bool, optional): Flag for reading numpy list of numeric values to be converted to numpy arrays. Defaults to False.
        read_include (bool, optional): Flag for enabling the `!include` constructor which enables reading others files just as embedded data. Defaults to True.
        n_list_flow_style (int, optional): Integer which states which shape of lists of numeric data that should be written with flow-style (e.g. `x: [1, 2, ...]`). Defaults to 1.

    Returns:
        ruamel.yaml.YAML: Instance with defaults as described above.
    """
    yaml_obj = YAML(
        typ=typ, pure=True
    )  # kenloen TODO: Can only make it work with the pure-python version (`pure=True`) as I can not figure out how to extract the file name for the file being
    yaml_obj.default_flow_style = False
    yaml_obj.width = 1e6
    yaml_obj.allow_unicode = False

    # Write nested list of numbers with flow-style
    def list_rep(dumper, data):
        try:
            npdata = np.asanyarray(data)  # Convert to numpy
            if np.issubdtype(npdata.dtype, np.number):  # Test if data is numeric
                if n_list_flow_style >= len(
                    npdata.shape
                ):  # Test if n_list_flow_style is larger or equal to array shape
                    return dumper.represent_sequence(
                        "tag:yaml.org,2002:seq", data, flow_style=True
                    )
        except ValueError:
            pass
        return dumper.represent_sequence(
            "tag:yaml.org,2002:seq", data, flow_style=False
        )

    yaml_obj.Representer.add_representer(list, list_rep)

    if write_numpy:
        # Convert numpy types to build in data types
        yaml_obj.Representer.add_multi_representer(
            np.str_, lambda dumper, data: dumper.represent_str(str(data))
        )
        yaml_obj.Representer.add_multi_representer(
            np.number,
            lambda dumper, data: dumper.represent_float(float(data)),
        )
        yaml_obj.Representer.add_multi_representer(
            np.integer, lambda dumper, data: dumper.represent_int(int(data))
        )

        # Convert numpy array to list
        def ndarray_rep(dumper, data):
            return list_rep(dumper, data.tolist())

        yaml_obj.Representer.add_representer(np.ndarray, ndarray_rep)

    def numpy_constructor(constructor, node):
        default_data = SafeConstructor.construct_sequence(constructor, node)
        try:
            if read_numpy:
                npdata = np.asarray(default_data)
                if np.issubdtype(npdata.dtype, np.number):
                    return npdata
            raise ValueError
        except ValueError:
            return default_data

    yaml_obj.Constructor.add_constructor("tag:yaml.org,2002:seq", numpy_constructor)

    if read_include:

        def include(constructor, node):
            filename = Path(constructor.loader.reader.stream.name).parent / node.value
            ext = os.path.splitext(filename)[1].lower()
            if ext in [".yaml", ".yml"]:
                return load_yaml(
                    filename, get_YAML()
                )  # TODO: Make `get_YAML()` dynamic to make it possible to update
            elif ext in [".nc"]:
                return ds2yml(xr.open_dataset(filename))
            else:
                raise ValueError(f"Unsupported file extension: {ext}")

        yaml_obj.constructor.add_constructor("!include", include)

    return yaml_obj


def load_yaml(filename: str, loader=None) -> dict:
    """
    Opens ``filename`` and loads the content into a dictionary with the ``get_YAML``
    function from ruamel.yaml.YAML.

    Args:
        filename (str): Path or file-handle to the local file to be loaded.
        loader (ruamel.yaml.YAML, optional): Defaults to ``get_YAML()``.

    Returns:
        dict: Dictionary representation of the YAML file given in ``filename``.
    """
    if loader is None:
        loader = get_YAML()
    return loader.load(filename)

def write_yaml(instance : dict, foutput : str) -> None:
    """
    Writes a dictionary to a YAML file using the ruamel.yaml library.

    Args:
        instance (dict): Dictionary to be written to the YAML file.
        foutput (str): Path to the output YAML file.

    Returns:
        None
    """
    instance = remove_numpy(instance)

    # Write yaml with updated values
    yaml = YAML()
    yaml.default_flow_style = None
    yaml.width = float("inf")
    yaml.indent(mapping=4, sequence=6, offset=3)
    yaml.allow_unicode = False
    with open(foutput, "w", encoding="utf-8") as f:
        yaml.dump(instance, f)

def remove_numpy(fst_vt : dict) -> dict:
    """
    Recursively converts numpy array elements within a nested dictionary to lists and ensures
    all values are simple types (float, int, dict, bool, str) for writing to a YAML file.

    Args:
        fst_vt (dict): The dictionary to process.

    Returns:
        dict: The processed dictionary with numpy arrays converted to lists and unsupported types to simple types.
    """

    def get_dict(vartree, branch):
        return reduce(operator.getitem, branch, vartree)

    # Define conversion dictionary for numpy types
    conversions = {
        np.int_: int,
        np.intc: int,
        np.intp: int,
        np.int8: int,
        np.int16: int,
        np.int32: int,
        np.int64: int,
        np.uint8: int,
        np.uint16: int,
        np.uint32: int,
        np.uint64: int,
        np.single: float,
        np.double: float,
        np.longdouble: float,
        np.csingle: float,
        np.cdouble: float,
        np.float16: float,
        np.float32: float,
        np.float64: float,
        np.complex64: float,
        np.complex128: float,
        np.bool_: bool,
        np.ndarray: lambda x: x.tolist(),
    }

    def loop_dict(vartree, branch):
        if not isinstance(vartree, dict):
            return fst_vt
        for var in vartree.keys():
            branch_i = copy.copy(branch)
            branch_i.append(var)
            if isinstance(vartree[var], dict):
                loop_dict(vartree[var], branch_i)
            else:
                current_value = get_dict(fst_vt, branch_i[:-1])[branch_i[-1]]
                data_type = type(current_value)
                if data_type in conversions:
                    get_dict(fst_vt, branch_i[:-1])[branch_i[-1]] = conversions[data_type](current_value)
                elif isinstance(current_value, (list, tuple)):
                    for i, item in enumerate(current_value):
                        current_value[i] = remove_numpy(item)

    # set fast variables to update values
    loop_dict(fst_vt, [])
    return fst_vt