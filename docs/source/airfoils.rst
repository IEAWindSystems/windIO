Airfoils
------------

**NOTE windIO has moved!** The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio

----

windIO describes the airfoils in terms of coordinates and polars. The yaml entry airfoils consists of a list of elements. 

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Airfoils
    :end-before: # Materials

:code:`name` : String
    Label identifying the airfoils

:code:`coordinates` : Object
    The airfoil :code:`coordinates` are specified here in the sub-fields :code:`x` and :code:`y`. :code:`x` and :code:`y` must have the same length. :code:`x` must be defined between 0, which corresponds to the leading edge, and 1, which corresponds to the trailing edge. Airfoil coordinates should be defined from trailing edge (:code:`x=1`) towards the suction side (mostly positive :code:`y` values), to leading edge (:code:`x=0`, :code:`y=0`), to the pressure side (mostly negative :code:`y`), and conclude at the trailing edge pressure side (:code:`x=1`). Flatback airfoils can be defined either open (:code:`x=1`, :code:`y!=0`) or closed (:code:`x=1`, :code:`y=0`).

:code:`relative_thickness` : Float
    Float defined between 0 (plate) and 1 (cylinder) to specify the relative thickness of the airfoil. This generates a small redundancy (it could be determined from the field coordinates), but it simplifies the converters.

:code:`aerodynamic_center` : Float 
    Float defined between 0 (leading edge) and 1 (trailing edge) to specify the chordwise coordinate of the aerodynamic center used to define the polars.

:code:`polars` : Object
List of one or more sets of polars for the airfoil. Each entry is marked with a dash (-) mark.
The field :code:`polars` must include the sub-fields :code:`configuration`, :code:`re`, :code:`c_l`, :code:`c_d`, and :code:`c_m`.

:code:`configuration` : String
    String to describe and identify the set of polars
:code:`re` : Float
    Reynolds number of the polars
:code:`c_l`: Object
    Lift coefficient as a function of angle of attack
:code:`c_d`: Object
    Drag coefficient as a function of angle of attack
:code:`c_m`: Object
    Moment coefficient as a function of angle of attack

:code:`c_l`, :code:`c_d`, and :code:`c_m` are defined via arrays :code:`grid` and :code:`values`, which must have the same length. :code:`grid` contains the angles of attack in radians and must be specified between -pi (-3.141592653589793) and pi (+3.141592653589793), while :code:`values` contains the coefficients.

The airfoils listed in this database are not all necessarily used in the blade. Only the ones called in :code:`airfoil_position' within :code:`outer_shape_bem` will actually be loaded to model the blade.
