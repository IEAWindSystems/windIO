
from __future__ import annotations
import yaml
import os
import copy
from pathlib import Path, PosixPath, WindowsPath
import jsonschema
import json
from urllib.parse import urljoin
import xarray as xr

### API design
import windIO.reference_library.plant
import windIO.reference_library.turbine
import windIO.schemas
import windIO.schemas.plant         # By importing plant and turbine here, we can use the schemas as windIO.schemas.plant and windIO.schemas.turbine
import windIO.schemas.turbine       # in the calling code after only importing windIO... import windIO; help(windIO.schemas.turbine)

plant_lib = windIO.reference_library.plant
turbine_lib = windIO.reference_library.turbine
schemas = windIO.schemas
### API design


class Loader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super().__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, self.__class__)
Loader.add_constructor('!include', Loader.include)

class XrResourceLoader(Loader):
    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        ext = os.path.splitext(filename)[1].lower()
        if ext in ['.yaml', '.yml']:
            with open(filename, 'r') as f:
                return yaml.load(f, XrResourceLoader)
        elif ext in ['.nc']:
            def fmt(v):
                if isinstance(v, dict):
                    return {k: fmt(v) for k, v in v.items() if fmt(v) != {}}
                elif isinstance(v, tuple):
                    return list(v)
                else:
                    return v

            def ds2yml(ds):
                d = ds.to_dict()
                return fmt({**{k: v['data'] for k, v in d['coords'].items()},
                            **d['data_vars']})
            return ds2yml(xr.open_dataset(filename))
XrResourceLoader.add_constructor('!include', XrResourceLoader.include)

def load_yaml(filename, loader=XrResourceLoader):
    with open(filename) as fid:
        return yaml.load(fid, loader)

def add_local_schemas_to(resolver, schema_folder, base_uri, schema_ext_lst=['.json', '.yaml', '.yml']):
    '''Function from https://gist.github.com/mrtj/d59812a981da17fbaa67b7de98ac3d4b#file-local_ref-py
    Add local schema instances to a resolver schema cache.

    Arguments:
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
                            schema_doc = yaml.safe_load(schema_file)

                    key = urljoin(base_uri, str(rel_path))
                    resolver.store[key] = schema_doc
                # except (ScannerError, ParserError):
                except Exception:
                    print("Reading %s failed" % file)

def validate(input: dict | str | Path, schema_type: str) -> None:
    """
    Validates a given windIO input based on the selected schema type.
    Raises jsonschema.exceptions.ValidationError if the input file is not valid.

    Args:
        input (dict | str | Path): Input to be validated. Could be a Python dictionary or
            a path to a yaml file.
        schema_type (str): Type of schema to be used for validation. This must map to one
            of the schema files available in the `schemas/plant` or `schemas/turbine` folders.
            Examples of valid schema types are 'plant/wind_energy_system' or
            'turbine/IEAontology_schema'.
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
    base_uri = 'https://www.example.com/schemas/'
    resolver = jsonschema.RefResolver(base_uri=base_uri, referrer=schema)
    schema_folder = Path(schema_file).parent
    add_local_schemas_to(resolver, schema_folder, base_uri)
    jsonschema.validate(data, schema, resolver=resolver)
