How to Build a Turbine Model
----------------------------

To build a turbine model, you need to create a YAML file that describes the turbine geometry and its components.
The YAML file should follow the schema defined in the `turbine_schema.yaml` file, which is located in the `windIO/schemas/turbine` directory.
The schema is written in YAML format and is used to validate the turbine model.
The schema is also used to generate the documentation for the turbine model.

It is usually best to start from an existing turbine model and modify it to fit your needs.

Here we will walk through the YAML file of the IEA-15MW turbine, which is located in the `windIO/examples/turbine/IEA-15-240-RWT-15MW.yaml` file.

The YAML file is divided into several sections, each describing a different part of the turbine model.
The top level sections are as follows:

- `windIO_version`: Version of windIO used.
- `assembly`: The field assembly includes nine entries that aim at describing the overall configuration of the wind turbine and its components.
- `components`: Specifications for individual components like blades, tower, and nacelle.
- `airfoils`: Database of airfoil coordinates, polars, and unsteady aero parameters.
- `materials`: Database of materials used in the turbine model.
- `control`: Control system.

Note that many text editors allow you to "fold" sections of the YAML file for easier navigation.
Folding collapses sections of the file, making it easier to focus on specific parts of the turbine model.
For example, you can fold the `components` section to hide its details while working on the `assembly` section.
Consult your text editor's documentation to learn how to use this feature.
Here is an example of the `assembly` section from the IEA-15MW turbine YAML file:

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 3-12

Next, let's look at the `components` section, which describes the individual components of the turbine.

Components
----------

Blade
~~~~~

The `blade` section of the turbine YAML file provides detailed specifications for the wind turbine blade. It is divided into the following subfields:

- `reference_axis`: Defines the reference axis of the blade in the blade root coordinate system. This axis is used as the basis for defining both the blade geometry and structural properties.
- `outer_shape`: Describes the external geometry of the blade, including airfoil profiles and their distribution along the blade span. It also includes the blending of airfoil polars.
- `structure`: Specifies the internal structure of the blade, including shear webs and composite material layers.
- `elastic_properties`: Defines the stiffness and inertia properties of the blade, which are critical for structural dynamic analysis.

reference_axis
++++++++++++++

An image representing the `reference_axis` of the blade is shown below.

.. image:: images/chord_reference_system.svg
   :width: 600 px
   :align: center
   :alt: Reference axis of the blade

This is how it looks for the IEA-15:

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 15-24


outer_shape
+++++++++++

Next, the :code:`outer_shape` is defined. Here, follow the  :doc:`detailed_turbine_documentation` for the details. 
It is important to note that each quantity that is distributed along the span is defined in terms of pairs of :code:`grid` and `values`.
The field `grid` maps the distribution of the quantity along the curved length of the reference axis,
while `values` defines the value of the quantity at each grid point.
The grid is defined in terms of a list of values, which are normalized to the 3D curvilinear blade length.

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 25-88

The outer aerodynamic 3D surface or structural outer mold line (OML) can be defined
in :code:`components.blade.outer_shape.surface`. It can be used to generate computational meshes for the internal blade structure or high-fidelity aerodynamic modelling.

To construct this surface, the following steps must be followed in the right order. 

1. From the outer_shape field, use :code:`rthick` or use PCHIP based on the master airfoils and the :code:`outer_shape.airfoils.spanwise_position` grid to interpolate airfoil cross-sections in between defined airfoils.
   Note that using spanwise_position in the windIO file requires the resolution of this grid to be quite fine, and airfoils with relative thickness above the typical 36% to be defined.
   Otherwise it is quite difficult to control the shape transition from the cylindrical root to the max chord.
   Also note that airfoils in the airfoils section should be interpolated onto a common grid based on normalized surface curve fraction using PCHIP, allowing point-wise interpolation between airfoils.
   Interpolating based on a common chord-wise discretization will result in very different airfoil shapes particularly for thick airfoils.
   Define the surface with an open trailing edge, since splining a discontinuous trailing edge will likely result in overshooting.
2. Scale airfoils by chord.
3. In the blade root coordinate system, apply :code:`section_offset_y` from the leading edge along the chord.
4. In the blade root coordinate system, apply :code:`section_offset_x` from the chord line normal to chord.
5. Compute and apply rotation matrix M to place airfoils orthonormal to local reference axis tangent, see below for details on this.
6. Apply x, y and z translations from the curved reference axis.

The transformation matrix for a cross-section is constructed as:

1. compute reference axis curve tangent unit vectors :math:`(t_x, t_y, t_z)` (preferably analytically using pchip derivatives)
2. compute rotation matrices for x- and y-rotations :math:`M_x` and :math:`M_y` from axis and angle, see https://en.wikipedia.org/wiki/Rotation_matrix "Rotation matrix from axis and angle"
3. :math:`M_{xy} = matmul(M_y, M_x)`
4. Compute twist correction :math:`r_z =  atan2(M_{xy}(0, 1), Mxy(0, 0))`. The twist correction is consistent with how the local chord reference system is defined in HAWC2, but this may be different in other aeroelastic tools.
5. :math:`r_z = twist + r_z`
6. Compute z-rotation matrix `M_z` as for step 2 from :math:`t_z` and :math:`r_z`
7. :math:`M = matmul(M_{xy}, M_z)`

The above definition of the transformation from local to blade reference frame is described in detail by `Li et al, 2024 <https://iopscience.iop.org/article/10.1088/1742-6596/2767/2/022033/pdf>`_.
Also see `Li et al, 2022 <https://wes.copernicus.org/articles/7/1341/2022/wes-7-1341-2022.pdf>`_.

This surface object is defined discretely as a block-structured surface grid with the following fields:

.. code-block:: yaml

    outer_shape:
        surface:
            grid: [0.0, 0.1, ...., 1.0]
            x: 
                - [...]  # x-coordinates for section 1
                - [...]  # x-coordinates for section nsec
            y:
                - [...]
                - [...]
            z:
                - [...]
                - [...]

which will map each coordinate direction to a :math:`(n_pts, nsec)` 2D array where :math:`n_pts` is the number of nodes in the cross-sections along the blade.
We define a local curvilinear mapping that in the spanwise direction follows the :code:`grid` used for the
:code:`reference_axis`.
In the direction along the local cross-section surface arc the field :code:`nd_arc_position` is defined as 0.0 at the trailing edge midpoint,
traveling along the suction side, to the leading edge and pressure side, and is 1.0 at the trailing edge midpoint, see below sketch.

.. image:: images/airfoil_nd_arc.svg
   :width: 600 px
   :align: center
   :alt: Definition of `nd_arc` along an airfoil's surface.

To compute the curve fraction, it is recommended to use an analytical spline evaluation of the curve as basis rather than the discrete points.

structure
+++++++++

The field :code:`components.blade.structure` contains the data to describe the internal composite structure of wind turbine blades.
Defining the structural geometry of a blade is a sophisticated process and the windIO ontology supports different parameterization types
that primarily targets conceptual design.
On the top level, the field :code:`blade.structure` has the sub-sections:

* :code:`anchors`: Defines anchor lines, planes and curves used to place the layup within the outer mold line (OML),
* :code:`webs`: (Optional) Defines the placement and geometry of the shear webs, 
* :code:`layers`: Defines all internal layers in terms of :code:`name`, :code:`material`, :code:`thickness`, number of plies :code:`n_plies`, :code:`fiber_orientation` (for composites), and position. 
* :code:`joints`: (Optional) Defines spanwise segmentation of blades.
* :code:`elastic_properties`: Defines the elastic properties of a beam-representation of the blade.

Anchors are used to define references for placement of layers, shear webs and other main features of the blade structure.


Below list summarizes the characteristics and rules for anchors:

* Anchors replace the previous positioning of layers using :code:`start_nd_arc` and :code:`end_nd_arc` in a layer field,
  and add the possibility of defining additional convenient planes and arc positions for placing layers.
* Anchors do not need to coincide with layer edges, but can define layer centers or other convenient positions,
* Anchors *must* define their non-dimensional arc position(s) along the cross-section surface using the :code:`start_nd_arc` and optionally :code:`end_nd_arc` fields,
* While arc positions can be anchored to other anchors, it must be possible to explicitly read the defined anchor arc positions from the windIO file,
  without geometric computations.
* Convenient schemas are available to define arc positions resulting from plane and ruled surface intersections.
* Anchors do not need to be defined along the entire spanwise grid of the blade.
* Anchors can cross and coincide, but this may pose challenges in mesh generation.
* The previously defined :code:`offset_y_pa` has been deprecated, and has been replaced with :code:`plane_intersection`.

The below list defines anchor names that are pre-defined but can be overwritten explicitly by the user:

:code:`name: TE`
    Trailing edge of the blade cross-sections, defined as the midpoint
    between the first and last point of the local cross-section, following the below sketch TE defines two values 
    :code:`start_nd_arc=0.0` and :code:`end_nd_arc=1.0`.
:code:`name: TE_SS`
    Suction side trailing edge of the blade cross-sections, defined by the
    first point of the local cross-section.
:code:`name: TE_PS`
    Pressure side trailing edge of the blade cross-sections, defined by the
    last point of the local cross-section.

In windIO v1.0, the leading-edge :code:`LE` could be used to place layers but not explicitly defined in terms of curve fraction.
However, in windIO 2.0, the user has to explicitly define this field as an anchor to avoid any ambiguities.

.. list-table::
   :widths: 400 400
   :header-rows: 0

   * - .. image:: images/airfoil_nd_arc.svg
          :width: 400 px
          :align: center
     - .. image:: images/airfoil_TE.svg
          :width: 400 px
          :align: center

Anchors are defined as a list and the :code:`name` and :code:`start_nd_arc` fields are required.
Depending on the anchor type :code:`end_nd_arc` can also be defined for the anchor.
Below we construct a user-defined leading edge mold split,
that only defines a single arc position along the span, :code:`start_nd_arc`:

.. code-block:: yaml

        -   name: le_mold_split
            start_nd_arc:
                grid: [0.0, 1.0]
                values: [0.47, 0.49]


An anchor can itself be positioned relative to another anchor using the :code:`offset_arc` field referencing the string name of
the anchor, combined with grid/value pair for the dimensioned offset. The offset can also be non-dimensional,
for which the :code:`offset_nd_arc` field is used.

.. code-block:: yaml

        -   name: te_reinforcement_ss
            start_nd_arc:
                grid: [0.0, 1.0]
                values: [0.13, 0.13]
            offset_arc:
                defines: start_nd_arc
                anchor:
                    name: TE_SS
                    handle: start_nd_arc
                grid: [0.0, 1.0]
                values: [0.5, 0.5]

The offset can be both positive or negative.


.. image:: images/airfoil_anchor+offset.svg
   :width: 600 px
   :align: center
   :alt: Example of anchor placement using `start_nd_arc` and `offset`.

Arc positions can be defined using the combined :code:`midpoint_nd_arc` and :code:`width` fields:

.. code-block:: yaml

        -   name: le_reinforcement
            start_nd_arc:
                grid: [0.0, 1.0]
                values: [0.47, 0.47]
            end_nd_arc:
                grid: [0.0, 1.0]
                values: [0.53, 0.53]
            midpoint_nd_arc:
                anchor:
                    name: LE
                    handle: start_nd_arc
            width:
                grid: [0.0, 1.0]
                values: [0.4, 0.4]
                defines:
                    - start_nd_arc
                    - end_nd_arc

.. image:: images/airfoil_midpoint_nd_arc.svg
   :width: 600 px
   :align: center
   :alt: Example of anchor placement using `midpoint_nd_arc` and `width`.


Anchors can also be defined from plane intersections, which is convenient for defining spar caps
that are typically straight or tapered, or shear webs that similarly intersect the surface with straight intersections.
Below we define the suction side spar cap, where the plane intersection defines the :code:`midpoint_nd_arc`,
which combined with the :code:`width` field results in :code:`start_nd_arc` and :code:`end_nd_arc` forming a constant width patch along the span
(note that the numbers in the below example are arbitrary).

.. code-block:: yaml

        -   name: spar_cap_ss
            start_nd_arc:
                grid: [0., 1.0]
                values: [0.31, 0.33]
            end_nd_arc:
                grid: [0.0, 1.0]
                values: [0.6, 0.6]
            plane_intersection:
                side: suction
                defines: midpoint_nd_arc
                plane_type1:
                    anchor_curve: reference_axis
                    anchors_nd_grid: [0.0, 1.0]
                    rotation: 0.0
                offset:
                    grid: [0.0, 1.0]
                    values: [0.4, 0.0]
            width:
                grid: [0.0, 1.0]
                values: [1.0, 1.0]
                defines:
                    - start_nd_arc
                    - end_nd_arc


.. image:: images/airfoil_cap_intersection.svg
   :width: 600 px
   :align: center
   :alt: Example of anchor placement using `midpoint_nd_arc` and `width`.

The above definition can also be split into two anchors, one that defines the midpoint of the spar cap, and a second one that uses this curve as an anchor, and defining a width,
computes the two edges of the cap.

.. code-block:: yaml

        -   name: spar_cap_ss_center
            start_nd_arc:
                grid: [0., 1.0]
                values: [0.45, 0.45]
            plane_intersection:
                side: suction
                defines: start_nd_arc
                plane_type1:
                    anchor_curve: reference_axis
                    anchors_nd_grid: [0.0, 1.0]
                    rotation: 0.0
                offset:
                    grid: [0.0, 1.0]
                    values: [0.0, 0.0]

        -   name: spar_cap_ss
            start_nd_arc:
                grid: [0., 1.0]
                values: [0.31, 0.33]
            end_nd_arc:
                grid: [0.0, 1.0]
                values: [0.6, 0.6]
            midpoint_nd_arc:
                anchor:
                    name: spar_cap_center
                    handle: start_nd_arc
            width:
                grid: [0.0, 1.0]
                values: [1.0, 1.0]
                defines:
                    - start_nd_arc
                    - end_nd_arc

Below we show how to define anchors for a shear web:

.. code-block:: yaml

        -   name: aft_web
            start_nd_arc:
                grid: [0., 1.0]
                values: [0.31, 0.33]
            end_nd_arc:
                grid: [0.0, 1.0]
                values: [0.6, 0.6]
            plane_intersection:
                side: both
                defines: start_end_nd_arc
                intersection_type1:
                    anchor_curve: reference_axis
                    anchors_nd_grid: [0.0, 1.0]
                    rotation: 8.0
                offset:
                    grid: [0.05, 0.95]
                    values: [0.4, 0.0]


.. image:: images/airfoil_web_intersection.svg
   :width: 600 px
   :align: center
   :alt: Example of plane_intersection used to define web placement.

The :code:`intersection_type1` intersection is performed as follows:

* Starting from the blade root coordinate system, rotate the lofted blade by the amount defined in :code:`rotation` around the blade `z`-axis using a right-handed rule.
* Interpolate the :code:`(x, y, z)` coordinates of the :code:`anchor_curve` curve at the :code:`anchors_nd_grid` non-dimensional arc positions,
  resulting in two points in space.
* Construct a plane spanning the two points, and with a normal vector in the y-z plane perpendicular to the line connecting the two points.
* Offset the plane along the plane normal vector by the amount defined in :code:`offset`. If the offset is not linear, the plane effectively becomes a ruled surface.
* Intersect the plane with the blade surface and compute the :code:`position_nd_arc` of the intersection curve along the span.

The :code:`side` indicates whether to intersect either the suction or pressure side, or both.
:code:`defines` lists the arc positions the intersection computes, with possible values :code:`start_end_nd_arc`, :code:`end_nd_arc`,
or :code:`midpoint_nd_arc` if it is used in combination with the :code:`width` field.

An alternative and also convenient method to define features in the blade is to intersect the blade with a ruled surface.
In the present implementation the ruled surface is constructed from an offset normal to the anchor curve in the y-z plane.

An example of this type of intersection is given below to compute the location of a
trailing edge shear web with a constant offset from the (curved) trailing edge.
The intersection type is referred to as :code:`intersection_type2`:

.. code-block:: yaml

        -   name: te_web
            start_nd_arc:
                grid: [0., 1.0]
                values: [0.05, 0.1]
            end_nd_arc:
                grid: [0., 1.0]
                values: [0.95, 0.9]
            plane_intersection:
                side: both
                defines: start_end_nd_arc
                intersection_type2:
                    anchor_curve: TE
                    rotation: 0.0
                offset:
                    grid: [0.0, 1.0]
                    values: [0.6, 0.6]

This intersection is performed as follows:

* Starting from the blade root coordinate system, rotate the lofted blade by the amount defined in :code:`rotation` around the blade root `z`-axis using a right-handed rule.
* In the y-z plane construct an offset curve normal to the anchor curve.
* Construct the ruled surface by extrapolating the offset curve along the :code:`x`-axis.
* Intersect the ruled surface with the blade surface and compute the :code:`position_nd_arc` of the intersection curve.

If the resulting intersection is not defined along the entire span of the blade, the last valid intersection point found should be used.
That would in the case of an intersection surface extending beyond the trailing edge, result in the curve coinciding with
the maximum :code:`y`-coordinate of the blade cross-sections, or conversely if it extends beyond the leading edge, the minimum :code:`y`-coordinates of the sections.

**Layers**

The :code:`layers` section defines the actual layup of typically composite materials in the blade.
The position of the layers is defined in terms of the anchors defined above, while the thickness and fiber orientation
are defined as spanwise and optionally chordwise distributions. An example of a layer definition is shown below:

.. code-block:: yaml

        -   name: TE_SS_filler
            material: foam
            thickness:
                grid: [0.05, 0.95]
                values: [0.05, 0.05]
            fiber_orientation:
                grid: [0.05, 0.95]
                values: [0.0, 0.0]
            start_nd_grid: 0.05
            end_nd_grid: 0.95
            start_nd_arc:
                anchor:
                    name: TE_SS
                    handle: start_nd_arc
            end_nd_arc:
                anchor:
                    name: spar_cap_ss
                    handle: start_nd_arc

**Shear web layups with layer drop-offs**

Shear webs are sandwich panels often composed of outer biaxial layers and a core material in-between.
windIO 2.x supports defining start and end arc extents of web layers referring to
their extent across the distance between the two shells. This is done by defining an :code:`anchors` field
for each web, with :code:`grid` / :code:`values` pairs where :code:`grid` is the spanwise non-dimensional curved length,
and :code:`values` is the non-dimensional arc length of the web.

.. code:: yaml

            webs:
               -  name: web1
                  start_nd_grid: 0.05
                  end_nd_grid: 0.98
                  start_nd_arc:
                      anchor:
                          name: web0
                          handle: start_nd_arc
                  end_nd_arc:
                      anchor:
                          name: web0
                          handle: end_nd_arc
                  anchors:
                     -  name: web1_shell_attachment
                        start_nd_arc:
                            grid: [0.05, 0.98]
                            values: [0.0, 0.0]
                        end_nd_arc:
                            grid: [0.05, 0.98]
                            values: [1.0, 1.0]
                     -  name: web1_core
                        start_nd_arc:
                            grid: [0.05, 0.98]
                            values: [0.05, 0.05]
                        end_nd_arc:
                            grid: [0.05, 0.98]
                            values: [0.95, 0.95]

In the :code:`layers` section, these anchors are referenced similar to the shell anchors:

.. code:: yaml

                 -  name: web1_skin00
                    web: web1
                    material: glass_biax
                    thickness:
                        grid: [0.05, 0.95]
                        values: [0.002, 0.002]
                    fiber_orientation:
                        grid: [0.05,  0.95]
                        values: [0.0,  0.0]
                    start_nd_grid: 0.05
                    end_nd_grid: 0.95
                    start_nd_arc:
                        anchor:
                            name: web1_shell_attachment
                            handle: start_nd_arc
                    end_nd_arc:
                        anchor:
                            name: web1_shell_attachment
                            handle: end_nd_arc

                 -  name: web1_filler
                    web: web1
                    material: medium_density_foam
                    thickness:
                        grid: [0.05, 0.95]
                        values: [0.002, 0.002]
                    fiber_orientation:
                        grid: [0.05,  0.95]
                        values: [0.0,  0.0]
                    start_nd_grid: 0.05
                    end_nd_grid: 0.95
                    start_nd_arc:
                        anchor:
                            name: web1_core
                            handle: start_nd_arc
                    end_nd_arc:
                        anchor:
                            name: web1_core
                            handle: end_nd_arc


**Web flanges**

To define web flanges the following section can be added to a web definition:

.. code-block:: yaml

    webs:
      - name: fore_web
        ...
        flanges:
          - type: L
            side: suction
            bondline:
                material: glue
                thickness:
                    grid: [0., 0.5, 1.0]
                    values: [0.03, 0.02, 0.01]
            start_nd_arc:
                anchor:
                    name: fore_web_anchor_ss
                    handle: start_nd_arc
            end_nd_arc:
                anchor:
                    name: fore_web_flange_anchor_ss
                    handle: start_nd_arc
          - type: L
            side: pressure
            bondline:
                material: glue
                thickness:
                    grid: [0., 0.5, 1.0]
                    values: [0.03, 0.02, 0.01]
            start_nd_arc:
                anchor:
                    name: fore_web_flange_anchor_ps
                    handle: start_nd_arc
            end_nd_arc:
                anchor:
                    name: fore_web_anchor_ps
                    handle: start_nd_arc

This feature is currently experimental, and details of the schema could be updated in future releases.

**Tapered thickness along the airfoil arc direction**

While it is often a good approximation that thickness of a composite layer is constant along the airfoil arc direction,
this is not the case for core material which is often tapered towards e.g. the trailing edge in a wind turbine blade.
windIO supports specifying thickness as a 2D array, where the first line defines the spanwise grid equivalent to the 1D grid normally used,
and following lines define the chordwise grid that represent the normalized arc distance between the layers' :code:`start_nd_arc` and its :code:`end_nd_arc`.

.. code-block:: yaml

    thickness:
        grid:
            - [0, 0.25, 0.75, 1]
            - [0.0, 0.0, 0.0, 0.0]
            - [0.25, 0.25, 0.25, 0.25]
            - [0.5, 0.5, 0.5, 0.5]
            - [0.75, 0.75, 0.75, 0.75]
            - [1.0, 1.0, 1.0, 1.0]
        values:
            - [0.0, 0.0, 0.0, 0.0]
            - [0.05, 0.05, 0.05, 0.05]
            - [0.10, 0.10, 0.10, 0.10]
            - [0.05, 0.05, 0.05, 0.05]
            - [0.0, 0.0, 0.0,0.0]

To taper core material linearly, the easiest approach would be to split the core into two separate patches, one with constant thickness,
and another with tapered thickness.


.. code-block:: yaml

    layers:
      - name: TE_SS_filler_taper
        material: foam
        start_nd_arc:
            anchor:
                name: te_reinforcement_ss
                handles: end_nd_arc
        end_nd_arc:
            anchor:
                name: TE_SS_filler_taper
                handles: start_nd_arc
        thickness:
            grid:
                - [0, 0.25, 0.75, 1]
                - [1.0, 1.0, 1.0, 1.0]
            values:
                - [0.0, 0.0, 0.0,0.0]
                - [0.05, 0.05, 0.05, 0.05]
      - name: TE_SS_filler
        material: foam
        start_nd_arc:
            anchor:
                name: TE_SS_filler_taper
                handles: start_nd_arc
        end_nd_arc:
            anchor:
                name: spar_cap_ss
                handles: start_nd_arc
        thickness:
            grid:
                - [0, 0.25, 0.75, 1]
            values:
                - [0.05, 0.05, 0.05, 0.05]

This feature is currently experimental, and details of the schema could be updated in future releases.

**Trailing edge adhesive**

The optional trailing edge adhesive fills the void on the inside of the shell at the trailing edge,
and its location is defined by four corners with references to anchors defined in the `anchors` section, two on the suction sice and two on the pressure side.
The exact topology of the trailing edge is often linked to the specific meshing tool used for the finite element analysis,
but can by the user be defined such that shell material wraps around trailing edge and meets at
an `nd_arc_position` of 0.0/1.0 (at the trailing edge midpoint), or left open requiring that the trailing edge bondline closes 
the trailing edge gap.

.. code-block:: yaml

        trailing_edge_adhesive:
            material: glue
            anchor_ss_start:
                name: TE_SS
                handle: start_nd_arc
            anchor_ss_end:
                name: TE_adhesive_ss_end
                handle: start_nd_arc
            anchor_ps_start:
                name: TE_PS
                handle: start_nd_arc
            anchor_ps_end:
                name: TE_adhesive_ps_end
                handle: start_nd_arc

This feature is currently experimental, and details of the schema could be updated in future releases.

**Complete example: IEA 15 MW RWT**

The :code:`structure` field often grows quite extensively. For the IEA-15MW turbine, it is defined as follows:

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 89-628


The fourth and last field of the :code:`blade` component is the :code:`elastic_properties`, whose subfields are:

- :code:`inertia_matrix`: Defines the inertia properties of the blade, including mass and moment of inertia.
- :code:`stiffness_matrix`: Defines the stiffness properties of the blade, including bending and torsional stiffness.
- :code:`structural_damping`: Defines the structural damping properties of the blade, currently in Rayleigh format :code:`mu`.
- :code:`point_mass`: Defines non-structural mass in the blade, such as lightning protection, root bolts etc, which is not defined or modelled as part of the composite structure.

The :code:`elastic_properties` field of the IEA-15MW turbine is defined as follows:

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 629-663


Hub
~~~

The `hub` section of the turbine YAML file provides detailed specifications for the wind turbine hub. Only a few fields are required,
namely :code:`diameter`, :code:`cone_angle`, and drag coefficient :code:`cd`.
Users can also decide to simply define the :code:`elastic_properties`.
The hub of the IEA-15MW turbine is defined as shown below.
Note that many inputs are optional and currently only used by NREL's systems engineering tool WISDEM, which was used to design the IEA-15MW turbine.

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 664-680

Drivetrain
~~~~~~~~~~

The :code:`drivetrain` section of the turbine YAML file provides detailed specifications for the wind turbine drivetrain. It includes the following subfields:
- :code:`outer_shape`: Defines the outer shape of the nacelle
- :code:`lss`: Defines the low-speed shaft
- :code:`hss`: Defines the high-speed shaft, when present
- :code:`gearbox`: Defines the gearbox, when present
- :code:`generator`: Defines the generator
- :code:`nose`: Defines the nose
- :code:`bedplate`: Defines the bedplate
- :code:`other_components`: Defines the auxiliary components of the nacelle
- :code:`elastic_properties`: Defines the equivalent elastic properties of the nacelle

Users should refer to the :doc:`detailed_turbine_documentation` for the details of each subfield. The drivetrain of the IEA-15MW turbine is defined as shown below. Note that many inputs are optional and currently only used by NREL's systems engineering tool WISDEM, which was used to design the IEA-15MW turbine.

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 736-835

Yaw
~~~
The :code:`yaw` section of the turbine YAML file provides detailed specifications for the wind turbine yaw system. Currently it only includes the equivalent :code:`elastic_properties` of the yaw system.
The schema for the yaw mass can be found `here <https://ieawindsystems.github.io/windIO/source/detailed_turbine_documentation.html#components_yaw>`_.

.. The yaw system of the IEA-15MW turbine is defined as shown below.

.. .. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
..     :language: yaml
..     :lines: 543-547

Tower
~~~~~
The :code:`tower` section of the turbine YAML file provides detailed specifications for the wind turbine tower. It includes the following subfields:

- :code:`reference_axis`: Defines the reference axis of the tower in the tower base coordinate system. This axis is used as the basis for defining both the tower geometry and structural properties.
- :code:`outer_shape`: Defines the outer shape of the tower
- :code:`structure`: Defines the inner structure of the tower
- :code:`elastic_properties`: Defines the equivalent elastic properties of the tower

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 681-706

Monopile
~~~~~~~~
The :code:`monopile` section of the turbine YAML file provides detailed specifications for the wind turbine monopile, when present. It includes the following subfields:

- :code:`reference_axis`: Defines the reference axis of the monopile in the tower base coordinate system. This axis is used as the basis for defining both the monopile geometry and structural properties.
- :code:`outer_shape`: Defines the outer shape of the monopile
- :code:`structure`: Defines the inner structure of the monopile
- :code:`elastic_properties`: Defines the equivalent elastic properties of the monopile

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 707-735

Floating platform
~~~~~~~~~~~~~~~~~
The :code:`floating_platform` section of the turbine YAML file provides detailed specifications for the wind turbine floating platform, when present. It includes the following subfields:

- :code:`transition_piece_mass`
- :code:`transition_piece_cost`
- :code:`joints`
- :code:`members`

The floating platform of the IEA-15MW turbine is defined as shown below.

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT_VolturnUS-S.yaml
    :language: yaml
    :lines: 807-999

Users should refer to the :doc:`detailed_turbine_documentation` for the details of each subfield.

Mooring
~~~~~~~
The `mooring` section of the turbine YAML file provides detailed specifications for the floating wind turbine mooring system, when present. It includes the following subfields:

- :code:`nodes`: Defines the nodes of the mooring system
- :code:`lines`: Defines the lines of the mooring system
- :code:`line_types`: Defines the characteristics of the lines
- :code:`anchor_types`: Defines the characteristics of the anchors

The floating platform of the IEA-15MW turbine is defined as shown below.

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT_VolturnUS-S.yaml
    :language: yaml
    :lines: 1000-1052

Users should refer to the :doc:`detailed_turbine_documentation` for the details of each subfield.

Airfoils
---------------
The :code:`airfoils` section of the turbine YAML file provides a database of airfoil coordinates, polars, and unsteady aero parameters. Each airfoil includes the following subfields:

- :code:`coordinates`: Defines the coordinates of the airfoils
- :code:`aerodynamic_center`: Defines the chordwise position of aerodynamic center of the airfoils
- :code:`rthick`: Defines the relative thickness of the airfoils
- :code:`polars`: Defines the polars of the airfoils

Multiple sets of :code:`polars` can be defined for each airfoil at varying conditions, for example distinguishing wind tunnel conditions and numerical results, or different roughness conditions. Also, for each configuration, multiple sets of polars can be defined at varying Reynolds number. Note that for every set of polars the user can opt to specify the unsteady parameters often required by aeroelastic models.

An example of the `FFA-W3-211` airfoil used in the IEA-15MW turbine is shown below.

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 836-994

Note that in this example only one configuration of polars at a single Re number is defined. The user can define multiple configurations by adding more entries to the `polars` field. The `polars` field is a list of dictionaries, where each dictionary represents a different configuration of polars. Multiple sets of polars for the same configuration under different Re numbers can be defined by adding more entries to the `re_sets` field. The `re_sets` field is a second list of dictionaries, where each dictionary represents polars at varying Reynolds.

Materials
---------

The :code:`materials` section of the turbine YAML file provides detailed specifications for the materials used in the wind turbine. The details of each entry are discussed in the page :doc:`detailed_turbine_documentation`. An example of the material `glass_biax` used in the IEA-15MW turbine is shown below.

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 995-1202

Control
-------
The :code:`control` section of the turbine YAML file provides detailed specifications for the wind turbine control system. It includes the following subfields:

- :code:`supervisory`: Defines the parameters of the supervisory control system
- :code:`pitch`: Defines the parameters of the pitch control system
- :code:`torque`: Defines the parameters of the torque control system
- :code:`yaw`: Defines the parameters of the yaw control system

The details of each field are discussed in the page :doc:`detailed_turbine_documentation`. An example of the :code:`control` section of the IEA-15MW turbine is shown below.

.. literalinclude:: ../../windIO/examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 1203-1217