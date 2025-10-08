import os
from io import StringIO
from pathlib import Path

import pytest
import numpy as np
import xarray as xr
import ruamel.yaml.error

import windIO
import windIO.yaml


def assert_equal_dicts(d1, d2):
    np.testing.assert_equal(type(d1), type(d2))
    for key, val in d1.items():
        if isinstance(val, dict):
            assert_equal_dicts(val, d2[key])
        elif isinstance(val, list):
            assert_equal_lists(val, d2[key])
        np.testing.assert_equal(type(val), type(d2[key]))
        np.testing.assert_equal(val, d2[key])


def assert_equal_lists(l1, l2):
    np.testing.assert_equal(type(l1), type(l2))
    np.testing.assert_equal(len(l1), len(l2))
    for val1, val2 in zip(l1, l2):
        if isinstance(val1, dict):
            assert_equal_dicts(val1, val2)
        elif isinstance(val1, list):
            assert_equal_lists(val1, val2)
        np.testing.assert_equal(type(val1), type(val2))
        np.testing.assert_equal(val1, val2)


def test_write_list_flow_style():
    data = {
        "a": [1, 2, 3],
        "b": [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]],
        "c": [1, "XY"],
        "d": ["1", "2", "3"],
        "e": [{"a": [1, 2], "b": [[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]}],
    }

    def get_yaml_str(data, flow_style=False):
        out = StringIO()
        yml_obj = windIO.YAML(typ="safe", pure=True)
        yml_obj.default_flow_style = flow_style
        yml_obj.indent(mapping=4, sequence=6, offset=3)
        yml_obj.dump(data, out)
        return out.getvalue()

    # WithOUT flow style
    out1 = StringIO()
    windIO.yaml._get_YAML(n_list_flow_style=0).dump(data, out1)
    str_data1 = out1.getvalue()
    assert str_data1 == get_yaml_str(data)

    # With flow-style for 1D numeric array
    out1 = StringIO()
    windIO.yaml._get_YAML(n_list_flow_style=1).dump(data, out1)
    str_data1 = out1.getvalue()
    n1D = 10
    i1D = 0
    for line in str_data1.split("\n"):
        if "[" in line:
            assert line.count("[") == 1 and line.count("]") == 1
            i1D += 1
    assert i1D == n1D

    # With flow-style for 2D numeric array
    out1 = StringIO()
    windIO.yaml._get_YAML(n_list_flow_style=2).dump(data, out1)
    str_data1 = out1.getvalue()
    n1D = 2
    i1D = 0
    n2D = 4
    i2D = 0
    for line in str_data1.split("\n"):
        if "[" in line:
            if line.count("[") > 1:
                assert line.count("[") == 3 and line.count("]") == 3
                i2D += 1
            else:
                assert line.count("[") == 1 and line.count("]") == 1
                i1D += 1
    assert i1D == n1D
    assert i2D == n2D

    # With flow-style for 3D numeric array
    out1 = StringIO()
    windIO.yaml._get_YAML(n_list_flow_style=3).dump(data, out1)
    str_data1 = out1.getvalue()
    n1D = 2
    i1D = 0
    n3D = 2
    i3D = 0
    for line in str_data1.split("\n"):
        if "[" in line:
            if line.count("[") > 1:
                assert line.count("[") == 7 and line.count("]") == 7
                i3D += 1
            else:
                assert line.count("[") == 1 and line.count("]") == 1
                i1D += 1
    assert i1D == n1D
    assert i2D == n2D


def test_write_numpy():

    # Data to test against
    test_data = dict(
        a=[0.1, 0.2],
        b=40,
        c=30.0,
        d="test",
        e=[[0.1, 0.2], [0.3, 0.4]],
        f=dict(a=[0.1, 0.2], b=40, c=30.0, d="test", e=[[0.1, 0.2], [0.3, 0.4]]),
        g=[5, [1.0, 3.0], "test"],
    )

    # Data containing numpy types
    din = dict(
        a=np.array([0.1, 0.2]),
        b=np.int16(40),
        c=np.float16(30.0),
        d=np.str_("test"),
        e=np.array([[0.1, 0.2], [0.3, 0.4]]),
        f=dict(
            a=np.array([0.1, 0.2]),
            b=np.int16(40),
            c=np.float16(30.0),
            d=np.str_("test"),
            e=np.array([[0.1, 0.2], [0.3, 0.4]]),
        ),
        g=[5, np.array([1.0, 3.0]), "test"],
    )

    # File StringIO "file" to write to
    tfile = StringIO()

    # Write data to "file"
    windIO.yaml._get_YAML().dump(din, tfile)
    # Reset file location
    tfile.seek(0)

    # Convert "file" to python data withOUT numpy reader
    dout = windIO.yaml._get_YAML().load(tfile)

    # Asserting that dicts are equal
    assert_equal_dicts(test_data, dout)


def test_include():
    base_path = Path(windIO.plant_ex.__file__).parent

    # Include YAML file
    filename = base_path / "plant_energy_site/IEA37_case_study_1_2_energy_site.yaml"
    # Manually inserting !include content
    with open(filename, "r") as f:
        lines = f.readlines()
        key_name, sub_filename = [el.strip() for el in lines[7].split("!include")]
        key_name = key_name.strip(":")
        lines.pop(7)
        out_wo_inc = windIO.yaml._get_YAML().load("\n".join(lines))
        out_wo_inc[key_name] = windIO.yaml._get_YAML().load(
            Path(filename).parent / sub_filename
        )

    out = windIO.load_yaml(filename)
    assert_equal_dicts(out, out_wo_inc)

    # Include netCFD file
    filename = base_path / "plant_energy_resource/GriddedResource_nc.yaml"
    with open(filename, "r") as f:
        lines = f.readlines()
        key_name, sub_filename = [el.strip() for el in lines[1].split("!include")]
        key_name = key_name.strip(":")
        lines.pop(1)
        out_wo_inc = windIO.yaml._get_YAML().load("\n".join(lines))
        out_wo_inc[key_name] = windIO.yaml._ds2yml(
            xr.open_dataset(Path(filename).parent / sub_filename)
        )
    out = windIO.yaml._get_YAML().load(
        base_path / "plant_energy_resource/GriddedResource_nc.yaml"
    )
    assert_equal_dicts(out, out_wo_inc)


def test_numpy_read():
    # Data to test against
    test_data = dict(
        a=[0.1, 0.2],
        b=[[0.1, 0.2], [0.3, 0.4]],
        c=dict(a=[0.1, 0.2], b=[[0.1, 0.2], [0.3, 0.4]]),
        d=[5, [1.0, 3.0], "test"],
        e=["test1", "test2"],
    )
    str_repr = StringIO()
    windIO.yaml._get_YAML().dump(test_data, str_repr)
    str_repr.seek(0)

    data = windIO.yaml._get_YAML(read_numpy=True).load(str_repr)
    assert isinstance(data["a"], np.ndarray), "`a` should be numpy array"
    assert len(data["a"].shape) == 1, "`a` shape should be 1D"
    assert isinstance(data["b"], np.ndarray), "`b` should be numpy array"
    assert len(data["b"].shape) == 2, "`b` shape should be 2D"
    assert isinstance(data["c"]["a"], np.ndarray), "`c.a` should be numpy array"
    assert len(data["c"]["a"].shape) == 1, "`c.a` shape should be 1D"
    assert isinstance(data["c"]["b"], np.ndarray), "`c.b` should be numpy array"
    assert len(data["c"]["b"].shape) == 2, "`c.b` shape should be 2D"
    assert isinstance(data["d"], list), "`d` should remain a list"
    assert isinstance(data["e"], list), "`e` should remain a list"


def test_load_yaml():
    yaml_pathlib_Path = Path(windIO.plant_ex.__file__).parent / "plant_energy_turbine" / "IEA37_10MW_turbine.yaml"
    # Load from Path instance
    assert isinstance(
        yaml_pathlib_Path, Path
    ), "`yaml_Path` should be a `pathlib.Path` instance"
    IEA_10_turb = windIO.load_yaml(yaml_pathlib_Path)
    windIO.validate(
        IEA_10_turb, "plant/turbine"
    )  # Testing that the loaded schema is valid

    # Load from string instance
    yaml_str = str(yaml_pathlib_Path)
    assert isinstance(yaml_str, str), "`yaml_str` should be a `str` instance"
    IEA_10_turb = windIO.load_yaml(yaml_str)
    windIO.validate(
        IEA_10_turb, "plant/turbine"
    )  # Testing that the loaded schema is valid

    # As a file-handle
    with open(yaml_pathlib_Path, "r") as file:
        IEA_10_turb = windIO.load_yaml(file)
        windIO.validate(
            IEA_10_turb, "plant/turbine"
        )  # Testing that the loaded schema is valid

    # Fail if not a path-like argument
    with pytest.raises(FileNotFoundError):
        not_a_filename = "this is not a valid filename"
        windIO.load_yaml(not_a_filename)

    with pytest.raises(ruamel.yaml.error.YAMLStreamError):
        windIO.load_yaml(dict())
