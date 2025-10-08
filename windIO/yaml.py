from __future__ import annotations

import os
from typing import Any
from pathlib import Path

import numpy as np
from ruamel.yaml import YAML
from ruamel.yaml.constructor import SafeConstructor
import netCDF4 # Importing netCFD to avoid warning: <frozen importlib._bootstrap>:241: RuntimeWarning: numpy.ndarray size changed, may indicate binary incompatibility. Expected 16 from C header, got 96 from PyObject
import xarray as xr


def _fmt(v: Any) -> dict | list | str | float | int:
    """
    Formats a dictionary appropriately for yaml.load by converting Tuples to Lists.

    Args:
        v (Any): Initially, a dictionary of inputs to format. Then, individual
            values within the dictionary.
    """
    if isinstance(v, dict):
        return {k: _fmt(v) for k, v in v.items() if _fmt(v) != {}}
    elif isinstance(v, tuple):
        return list(v)
    else:
        return v


def _ds2yml(ds: xr.Dataset) -> dict:
    """
    Converts the input xr.Dataset to a format compatible with yaml.load.

    Args:
        ds (xr.Dataset): NetCDF data loaded as a xr.Dataset
    """
    d = ds.to_dict()
    return _fmt(
        {
            **{k: v["data"] for k, v in d["coords"].items()},
            **d["data_vars"],
        }
    )


def _get_YAML(
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
    yaml_obj.indent(mapping=4, sequence=6, offset=3)
    yaml_obj.sort_base_mapping_type_on_output = False

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
                    filename, _get_YAML()
                )  # TODO: Make `get_YAML()` dynamic to make it possible to update
            elif ext in [".nc"]:
                return _ds2yml(xr.open_dataset(filename))
            else:
                raise ValueError(f"Unsupported file extension: {ext}")

        yaml_obj.constructor.add_constructor("!include", include)

    return yaml_obj


def load_yaml(filename: str | Path | os.PathLike, loader=None) -> dict:
    """
    Opens ``filename`` and loads the content into a dictionary with the ``_get_YAML``
    function from ruamel.yaml.YAML.

    Args:
        filename (str | Path | os.PathLike): Path or file-handle to the local file to be loaded or string path to the file.
        loader (ruamel.yaml.YAML, optional): Defaults to SafeLoader.

    Returns:
        dict: Dictionary representation of the YAML file given in ``filename``.
    """
    if loader is None:
        loader = _get_YAML()

    if isinstance(filename, str):
        filename = Path(filename)

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
    # Write yaml with updated values
    yaml = _get_YAML()
    with open(foutput, "w", encoding="utf-8") as f:
        yaml.dump(instance, f)
