[![Build Status](https://github.com/IEAWindSystems/windIO/workflows/CI_windIO/badge.svg?branch=master)](https://github.com/IEAWindSystems/windIO/actions)
[![Documentation Status](https://readthedocs.org/projects/windio/badge/?version=latest)](https://windio.readthedocs.io/en/latest/)

# windIO

Frameworks defining the inputs and outputs for systems engineering MDAO of wind turbine and plants. The framework was developed by the IEA Wind Task 37 team within Work Package 1.

Author: [IEA Wind Task 37 Team](mailto:pietro.bortolotti@nrel.gov)

## Version

This software is a version 1.0

## Documentation and citation

The online documentation can be accessed here <https://ieawindsystems.github.io/windio>

If you use this model in your research or publications, please cite this [IEA technical report](https://doi.org/10.2172/1868328):

    @article{osti_1868328,
    title = {System Modeling Frameworks for Wind Turbines and Plants: Review and Requirements Specifications},
    author = {Bortolotti, Pietro and Bay, Christopher and Barter, Garrett and Gaertner, Evan and Dykes, Katherine and McWilliam, Michael and Friis-Moller, Mikkel and Molgaard Pedersen, Mads and Zahle, Frederik},
    doi = {10.2172/1868328},
    place = {United States},
    year = {2022},
    month = {5}
    }

## Example and unit testing

An example of a turbine yaml file can be found here test/turbine_example.yaml.

The file is validated using the jsonschema library (https://github.com/Julian/jsonschema) and it is unit-tested on GitHub Actions. 
