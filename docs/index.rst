.. windIO documentation master file, created by
   sphinx-quickstart on Mon May 11 17:30:20 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

windIO has moved!
=================

The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio


Welcome to windIO's documentation!
----------------------------------

.. only:: html

The repository defines two frameworks defining the inputs and outputs for systems engineering MDAO of wind turbine and plants. The github repository is `here <https://github.com/IEAWindTask37/windIO>`_.
The frameworks are implemented in two yaml-schemas, one for the turbine and one for the plant, to enforce an ontology of how data should be organized. The reference wind turbines designed within work package 2 of the IEA Wind Task 37 are checked against the schema through unit testing. You can access the yaml files at the following links `IEA onshore 3.4 MW  <https://github.com/IEAWindTask37/IEA-3.4-130-RWT/blob/master/yaml/IEA-3.4-130-RWT.yaml>`_, `IEA offshore 10.0 MW  <https://github.com/IEAWindTask37/IEA-10.0-198-RWT/blob/master/yaml/IEA-10-198-RWT.yaml>`_, and `IEA floating 15.0 MW  <https://github.com/IEAWindTask37/IEA-15-240-RWT/blob/master/WT_Ontology/IEA-15-240-RWT.yaml>`_.

    Author: `IEA Wind Task 37 Team <mailto:pietro.bortolotti@nrel.gov>`_

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   source/turbine
   source/plant


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
