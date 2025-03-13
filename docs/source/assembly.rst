*******************
Assembly
*******************

**NOTE windIO has moved!** The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio

----

The field :code:`assembly` includes five entries that aim at describing the overall configuration of the wind turbine:

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Assembly
    :end-before: # Control

:code:`turbine_class` : String 
    IEA wind class. The entry should be :code:`I`, :code:`II`, :code:`III`, or :code:`IV`. 

:code:`turbulence_class` : String 
    IEA turbulence class. The entry should be :code:`A`, :code:`B`, or :code:`C`. 

:code:`drivetrain` : String 
    Drivetrain configuration. This is intended to inform a automated interpreter of the yaml about the data specified in the field :code:`drivetrain`

:code:`rotor_orientation` : String 
    Switch between :code:`upwind` and :code:`downwind` rotor configurations.

:code:`number_of_blades` : Integer 
    Number of rotor blades.
