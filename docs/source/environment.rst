Environment
------------

**NOTE windIO has moved!** The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio

----

The field :code:`environment` includes the data characterizing air and water.

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Environment
    :end-before: # Costs

:code:`air_density` : Float, kg/m3
    Density of air. 
:code:`air_dyn_viscosity` : Float, kg/(m*s)
    Dynamic viscosity of air.
:code:`weib_shape_parameter` : Float 
    Shape parameter of the Weibull wind distribution. 
:code:`air_speed_sound` : Float, m/s
    Speed of sound in air. 
:code:`shear_exp` : Float 
    Shear exponent of the wind.
:code:`water_density` : Float, kg/m3
    Density of water. 
:code:`water_dyn_viscosity` : Float, kg/(m*s)
    Dynamic viscosity of air. 
:code:`soil_shear_modulus` : Float, Pa
    Shear modulus of the soil. 
:code:`soil_poisson` : Float
    Poisson ratio of the soil. 