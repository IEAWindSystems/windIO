
Blade
================

**NOTE windIO has moved!** The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio

----

The component :code:`blade` includes three subcomponents, namely :code:`outer_shape_bem`, :code:`elastic_properties_mb`, and :code:`internal_structure_2d_fem`. A fourth subfield :code:`lofted_shape` is in progress.

All distributed quantities, such as blade chord or the thickness of a structural component, are expressed in terms of pair arrays :code:`grid` and :code:`values`, which must have a minimum length of two elements and the same size. :code:`grid` is defined nondimensional between 0 (root) and 1 (tip) along the, possibly curved, :code:`reference_axis`.

outer_shape_bem 
-------------------
:code:`outer_shape_bem` consists of a dictionary containing the data for blade BEM-based aerodynamics. 

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Blade - Outer Shape BEM
    :end-before: # Blade - Elastic properties

:code:`airfoil_position'labels` : Array of strings 
    The array :code:`labels` specifies the names of the airfoils to be placed along the blade. The positions are specified in the field :code:`grid`. The two arrays must share the same length and to keep an airfoil constant along blade span, this must be defined twice. The :code:`labels` must match the :code:`names` of the airfoils listed in the top level :code:`airfoils`. In between airfoils, the recommended interpolation scheme for both coordinates and polars is the Piecewise Cubic Hermite Interpolating Polynomial (PCHIP), which is implemented in `Matlab <https://www.mathworks.com/help/matlab/ref/pchip.html>`_ and in the Python library `SciPy  <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.PchipInterpolator.html>`_.

:code:`chord.values` : Array of floats, m 
    The array :code:`values` specifies the chord along blade span.

:code:`twist.values` : Array of floats, rad 
    The array :code:`values` specifies the aerodynamic twist along blade span. In the example provided above, a json pointer &twist is defined, which will be used to rotate composite layers in :code:`internal_structure_2d_fem`. Remember, the unit of measure of the twist is not degrees!

:code:`pitch_axis.values` : Array of floats 
    The array :code:`values` specifies the positions along blade span of the position of the airfoil in respect to the blade reference axis. A value of 0 means that the reference axis, around which the blade pitches and twists, crosses the airfoil at the leading edge, while a value of 1 corresponds to the trailing edge. Standard value oscillate between 0.5 for the blade root cylinder and 0.25. These are the values reported in the example.

:code:`reference_axis` : Object
    The field :code:`reference_axis` describe the three-dimensional shape of the reference axis of the blade via three sub-fields, namely :code:`x`, :code:`y`, and :code:`z`. The three sub-fields contain the pairs of arrays :code:`grid` and :code:`values`. The former is nondimensional, while the latter is expressed in meters.

    The coordinate system is the one of `BeamDyn  <https://openfast.readthedocs.io/en/master/source/user/beamdyn/input_files.html#beamdyn-primary-input-file>`_ of OpenFAST and it is shown in the figure below. 

    .. image:: images/reference_axis.jpg
        :width: 800
    
    The consequences of this reference system is that standard wind turbine blades have positive twist inboard and close to zero or even slightly negative twist outboard, zero or negative x values for standard prebent blades, and positive y values for backward swept blades. The blade main direction is expressed along z, and total blade length must be computed integrating the fields x, y, and z three-dimensionally.



elastic properties mb 
-----------------------
The equivalent elastic properties of the blade are defined in :code:`elastic_properties_mb`. Here, 6x6 stiffness and mass matrices are defined in the same reference system used by the solver `BeamDyn  <https://openfast.readthedocs.io/en/master/source/user/beamdyn/input_files.html#beamdyn-primary-input-file>`_ of OpenFAST. Out of 36 entries of the matrices, given the symmetry, the yaml file requires the definition of only 21 values as inputs. These are defined row by row, so first the six elements of the first row, then the five elements of the second row, and so on finishing with the sixth element of the sixth row.
For a blade without extra-diagonal, the stiffness and mass matrices look like this:

K = [Kflap, 0, 0, 0, 0, 0, Kedge, 0, 0, 0,0, EA, 0, 0, 0, EIedge, 0, 0, EIflap, 0, GJ]

M = [m, 0, 0, 0, 0, -mYcm, m, 0, 0, 0,mXcm, m, mYcm, -mXcm, 0, iedge, -icp, 0, iflap, 0, iplr]

where KShrEdg and KShrFlp are the edge and flap shear stiffnesses, respectively; EA is the extension stiffness; EIEdg and EIFlp are the edge and flap stiffnesses, respectively; GJ is the torsional stiffness, m is the mass density per unit span, Xcm and Ycm are the local coordinates of the sectional center of mass, iedge and iflap are the edge and flap mass moments of inertia per unit span, iplr is the polar moment of inertia per unit span, and finally icp is the sectional cross product of inertia per unit span. Please note that for beam-like structures iplr must be equal to iedge plus iflap.

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Blade - Elastic properties
    :end-before: # Internal Structure 2D FEM

internal structure 2d_fem
---------------------------
The field :code:`internal_structure_2d_fem` contains the data to describe the internal structure of standard wind turbine blades. This is a fairly sophisticated process and the ontology proposed in this work supports different definitions. On the top level, the field :code:`internal_structure_2d_fem` has three sub-components, namely the :code:`reference_axis`, which is usually defined equal to the :code:`reference_axis` in the field :code:`outer_shape_bem`, the :code:`webs`, where the positions of the shear webs are defined, and the :code:`layers`, which describe all internal layers in terms of :code:`name`, :code:`material`, :code:`thickness`, number of plies :code:`n_plies`, :code:`fiber_orientation` (for composites), and position in the two-dimensional sections. 

.. literalinclude:: ../../test/top_level.yaml
    :start-after: # Structure
    :end-before: # EOF3


webs
^^^^^^^^^^
The field :code:`webs` consists of a list of entries, each representing a shear web defined in terms of :code:`name` and position.

:code:`name` : String
    String that identifies the web.

The first (and usually most convenient) way to define the position of a shear web is by defining the fields :code:`rotation` and :code:`offset_y_pa`, which are distributed along span and are therefore described in terms of :code:`grid` and :code:`values` pairs.

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Webs
    :end-before: # Web 2

:code:`rotation.values` : Array of floats, rad 
    The rotation defines the angle between the chord line and the y axis and it has the opposite sign of the twist. For shear webs perpendicular to the chord line in the section(s) where twist is zero, it is easiest to simply use the keyword fixed: twist. In the example provided above, a json pointer &twist is defined.
    
:code:`offset_y_pa.values` : Array of floats, m 
    The field offset_y_pa defines the distance in meters along the y axis between the pitch axis and the plane of the shear web and it is defined along y. 


Blades with straight shear webs will always have the field rotation equal to the twist plus/minus a constant angle and, assuming a non-swept blade (zero values in the blade y reference axis), a linear field offset_y_pa.

    .. image:: images/web1.jpg
        :width: 800

The second approach to define the position of a shear web is by defining the fields :code:`start_nd_arc` and :code:`end_nd_arc`, which are also distributed along span and are therefore also described in terms of :code:`grid` and :code:`values` pairs.

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Web 2
    :end-before: # Layers

:code:`start_nd_arc.values` : Array of floats
    The field defines the nondimensional position along the arc of a 2D blade section, where 0 represents the trailing edge on the suction side and 1 the trailing edge on the pressure side. For flatback airfoils, the start (s = 0) and end (s = 1) nondimensional coordinate s is defined in the midpoint between suction and pressure sides. The shear webs have the field :code:`start_nd_arc` on the suction side, so usually smaller than 0.5, which approximately correspond to the leading edge.
    
:code:`end_nd_arc.values` : Array of floats
    On the opposite, the shear webs have the field :code:`end_nd_arc` on the pressure side, so usually between 0.5 and 1.
     
    .. image:: images/web2.jpg
        :width: 400



layers
^^^^^^^^^^^^^
The sub-field :code:`layers` define the layers of the wind turbine blade. In most cases, these are layers of composite materials. Each layer is defined by the following entries.

:code:`name` : String
    String that identifies the layer.
:code:`material` : String
    String that identifies the material of the layer. The material and its properties must be defined in the top-level :code:`materials`.
:code:`thickness` : Float, m
    Dimensional thickness of the laminate, expressed in meters. This value is modeled constant along the section. To define ply drops along the 2D surface, the user is therefore required to define multiple layers, possibly ply by ply when many ply drops exist.
:code:`n_plies` : Float
    In addition or in alternative to the dimensional thickness, the discrete number of plies of a composite laminate can be defined by the user. Notably, the ply thickness is a material property (not a layer property) and it is defined in the top-level field materials.
:code:`fiber_orientation` : Float, rad
    For composite laminates, the orientation of the fibers in radians can be specified. Looking from blade root, positive angles represent a rotation of the fibers towards the leading edge of the blade. Note that the angles are in respect to the cross section local reference system, not the reference system at blade root. 

The position of the layer in the 2D section can be specified in various ways. If nothing is defined, this assumes that the sub-field :code:`start_nd_arc` is equal to 0 and the sub-field :code:`end_nd_arc` is equal to 1. This means that the layer wraps the whole section, such as in the example below for the outer paint. This definition of a layer should be used also for example for the outer shell skin, which tyoically wraps the whole section.

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Layer 1
    :end-before: # Layer 2

The most convenient approach to define the position of spar caps mimics the definition of the shear webs, adding the width and side that define the width of the layer in meters and the side where the layer is located, either “pressure” or “suction”. 

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Layer 3
    :end-before: # Layer 4

:code:`width.values` : Array of floats, m 
    The field width defines the width in meters along the arc of the layer. 

:code:`side` : String
    The field side is string that can be either :code:`suction` or :code:`pressure`, defining the side where a layer is defined.

    .. image:: images/layer1.jpg
        :width: 800

To define reinforcements, the best way is usually to define the width, in meters, and the midpoint, named :code:`midpoint_nd_arc` and defined nondimensional between 0 and 1. Converters should be able to look for the leading edge, marked as LE.

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Layer 4
    :end-before: # Layer 5

:code:`midpoint_nd_arc.values` : Array of floats
    Coordinate along the arc of the midpoint of the layer. 

Similar combinations can be constructed with the combination of :code:`width` and :code:`start_nd_arc` or :code:`end_nd_arc`.

    .. image:: images/layer2.jpg
        :width: 800

Finally, for composite layers belonging to the shear webs, a tag :code:`web` should contain the name of the web. The layers are then modeled from leading edge to trailing edge in the order they were specified.

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Web layer
    :end-before: # Hub

Lofted Shape 
-------------------
This is work in progress. :code:`lofted_shape` will consist of a dictionary containing the 3D points describing the outer lofted shape of the blade 

