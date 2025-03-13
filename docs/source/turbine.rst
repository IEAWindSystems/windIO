Turbine
------------

**NOTE windIO has moved!** The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio

----

The wind turbine ontology, which is currently implemented in YAML and supported by a JSON schema, is developed defining nine top-level entries.

.. literalinclude:: ../../test/top_level.yaml
    :start-after: # Top level entries of the IEA Wind Task 37 wind turbine ontology
    :end-before: # EOF


:code:`name` : String
    Unique identifier of the wind turbine model
    
:code:`description` : String
    Text field to describe the wind turbine, the changes to previous versions, etc,
    
:code:`components` : Object
    Nested dictionary structure of components composing the wind turbine assembly
    
:code:`airfoils` : List
    List of airfoils, each being a dictionary that can be referenced at the component level
    
:code:`materials` : List
    List of materials, each being a dictionary that can be referenced at the component level
    
:code:`assembly` : Object
    Dictionary reporting the macro parameters of the wind turbine assembly
    
:code:`actuators` : Object
    Dictionary reporting the data describing the wind turbine actuators
    
:code:`control` : Object
    Dictionary reporting the data describing the wind turbine control
    
:code:`environment` : Object
    Dictionary reporting the data describing the environment where the wind turbine operates
    
:code:`costs` : Object
    Dictionary reporting the main inputs for a levelized cost of energy analysis.

In the pages below a detailed explanation of the sub-fields of each entry is provided (:code:`name` and :code:`description` are not listed given their simplicity).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   components
   airfoils
   materials
   assembly
   control
   environment
   costs
