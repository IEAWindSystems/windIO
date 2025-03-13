Costs
------------

**NOTE windIO has moved!** The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio

----

The field :code:`costs` includes the data to conduct an LCOE analysis of the wind turbine. The structure of the data is based on the analysis presented in the report https://www.nrel.gov/docs/fy20osti/74598.pdf

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Costs
    :end-before: # EOF

:code:`wake_loss_factor` : Float
    Loss factor to account for wind park losses, such as wake losses. This is used to convert the annual energy production of the turbine to the annual energy production of the wind plant.
:code:`fixed_charge_rate` : Float 
    Fixed charge rate for the project.
:code:`bos_per_kW` : Float, $/kW
    Balance of station costs.
:code:`opex_per_kW` : Float, $/kW
    Operational expenditures.
:code:`turbine_number` : Integer
    Number of turbines in the wind park.