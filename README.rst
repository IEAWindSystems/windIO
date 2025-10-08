.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.15191297.svg
  :target: https://doi.org/10.5281/zenodo.15191297
  :alt: DOI

.. image:: docs/logo/windIO_logo.png
   :alt: windIO Logo
   :align: center
   :width: 100px

windIO: a community-focused data I/O format for wind energy systems
===================================================================

windIO is a data format for inputs and outputs to wind energy system computational models.
Historically, it has focused on systems engineering models, but it has been adopted in other
topic areas of wind energy modeling, as well.
The windIO data format is a community-focused effort to standardize the data format for wind energy
system models, and we encourage collaboration.
The github repository is at https://github.com/IEAWindSystems/windIO and the
online documentation is at https://ieawindsystems.github.io/windIO.

The windIO repository includes the following:

- Schema defining windIO components describing wind turbines and wind plants
- Python library for validating files relative to the schema and loading the data into a Python dictionary
- windIO input files for test-case wind turbine and wind plant models

Reference wind turbines designed within the IEA Wind Systems Engineering Task
are available at the following links:

- `IEA onshore 3.4 MW  <https://github.com/IEAWindTask37/IEA-3.4-130-RWT/blob/master/yaml/IEA-3.4-130-RWT.yaml>`_
- `IEA offshore 10.0 MW  <https://github.com/IEAWindTask37/IEA-10.0-198-RWT/blob/master/yaml/IEA-10-198-RWT.yaml>`_
- `IEA floating 15.0 MW  <https://github.com/IEAWindTask37/IEA-15-240-RWT/blob/master/WT_Ontology/IEA-15-240-RWT.yaml>`_
- `IEA 22-MW offshore <https://github.com/IEAWindSystems/IEA-22-280-RWT>`_
- `IEA Wind 740-10-MW Reference Offshore Wind Plants <https://github.com/IEAWindSystems/IEA-Wind-740-10-ROWP/blob/main/README.md>`_

If you use this model in your research or publications, please cite the DOI from Zenodo:

DOI: `10.5281/zenodo.15191297 <https://doi.org/10.5281/zenodo.15191297>`_

Alternatively, you can cite this older `IEA technical report <https://doi.org/10.2172/1868328>`_:

   @article{osti_1868328,
      title = {System Modeling Frameworks for Wind Turbines and Plants: Review and Requirements Specifications},
      author = {Bortolotti, Pietro and Bay, Christopher and Barter, Garrett and Gaertner, Evan and Dykes, Katherine and McWilliam, Michael and Friis-Moller, Mikkel and Molgaard Pedersen, Mads and Zahle, Frederik},
      doi = {10.2172/1868328},
      place = {United States},
      year = {2022},
      month = {5}
   }

Author: `IEA Wind Task 37 and 55 Teams <mailto:pietro.bortolotti@nrel.gov>`_

Installation
------------

windIO is typically included as a dependency in software that uses the windIO data format, so
users will normally not need to install it directly.
However, it can be useful to install the windIO package to access version converters or during
integration into a software package.
In that case, windIO can be installed from PyPI with the following command:

.. code-block:: bash

   pip install windIO

Supporting windIO in your software
----------------------------------

The windIO data format is defined by the schemas included in this repository.
In order for a software to support windIO, it must support the data as described in the schemas
and use the included functions to validate the data.
windIO should be included as a dependency.
It is distributed through PyPI and can be installed as a package with pip.
The suggested method of incorporating windIO into your code is:

.. code-block:: python

   import windIO

   # Other code here

   data = windIO.validate(input="path/to/input.yaml", schema_type="plant/wind_energy_system <for example>")

   # Conversion to your software's data structures here

Note that an optional argument to populate the input file with default values from the schema is available:

.. code-block:: python

   data = windIO.validate(input="path/to/input.yaml", schema_type="plant/wind_energy_system <for example>", defaults=True)