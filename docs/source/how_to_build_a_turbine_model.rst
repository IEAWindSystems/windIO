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
- `assembly`: The field assembly includes nine entries that aim at describing the overall configuration of the wind turbine
  and its components.
- `components`: Specifications for individual components like blades, tower, and nacelle.
- `airfoils`: Database of airfoil coordinates, polars, and unsteady aero parameters.
- `materials`: Database of materials used in the turbine model.
- `control`: Control system.
- `environment`: Environmental conditions and parameters.
- `bos`: Balance of system inputs.
- `costs`: CapEx and OpEx cost inputs.

Note that many text editors allow you to "fold" sections of the YAML file for easier navigation.
Folding collapses sections of the file, making it easier to focus on specific parts of the turbine model.
For example, you can fold the `components` section to hide its details while working on the `assembly` section.
Consult your text editor's documentation to learn how to use this feature.
H
ere is an example of the `assembly` section from the IEA-15MW turbine YAML file:

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
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

An image representing the `reference_axis` of the blade is shown below.

.. image:: source/image/reference_axis.png
   :width: 600 px
   :align: center
   :alt: Reference axis of the blade

This is how it looks for the IEA-15:

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 15-24


Next, the `outer_shape` is defined. Here, follow the  :doc:`detailed_turbine_documentation` for the details. It is important to note that each quantity that is distributed along the span is defined in terms of pairs of `grid` and `values`. The field `grid` maps the distribution of the quantity along the span, while `values` defines the value of the quantity at each grid point. The grid is defined in terms of a list of values, which are normalized to the 3D curvilinear blade length.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 25-88

The `structure` section describes the inner structure of the blade. It includes the two fields:
- `webs`
- `layers`

The `webs` field describes the shear webs of the blade, whereas the `layers` field describes the layers of composite materials that make up the blade. Each layer has an associated material and thickness. `layers` can belong to the outer mold line as well as to the shear webs. In the latter case they have a `web` tag.
The definition of the chordwise positions of layers and webs is done in different ways. The primary way to define the position of a web or of a layer is to define its `start_nd_arc` and `end_nd_arc` positions. These are the normalized distance along the blade length from the trailing edge suction side to the trailing edge pressure side. The `start_nd_arc` and `end_nd_arc` values are defined in terms of a list of values, which are apped to the usual `grid` that follows the 3D curvilinear blade length.

The image below shows `start_nd_arc` and `end_nd_arc`:

.. image:: source/image/structure1.png
   :width: 600 px
   :align: center
   :alt: Definition of `start_nd_arc` and `end_nd_arc`


The `structure` field often grows quite extensively. For the IEA-15MW turbine, it is defined as follows:

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 89-382

The fourth and last field of the `blade` component is the `elastic_properties`, whose subfields are:
- `inertia_matrix`: Defines the inertia properties of the blade, including mass and moment of inertia.
- `stiffness_matrix`: Defines the stiffness properties of the blade, including bending and torsional stiffness.
- `structural_damping`: Defines the structural damping properties of the blade, currently in Rayleigh format `mu`.

The `elastic_properties` field of the IEA-15MW turbine is defined as follows:

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 383-417

Hub
~~~

The `hub` section of the turbine YAML file provides detailed specifications for the wind turbine hub. Only a few fields are required, namely `diameter`, `cone_angle`, and drag coefficient `cd`. Users can also decide to simply define the `elastic_properties`. The hub of the IEA-15MW turbine is defined as shown below. Note that many inputs are optional and currently only used by NREL's systems engineering tool WISDEM, which was used to design the IEA-15MW turbine.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 418-438

Drivetrain
~~~~~~~~~~
The `drivetrain` section of the turbine YAML file provides detailed specifications for the wind turbine drivetrain. It includes the following subfields:
- `outer_shape`: Defines the outer shape of the nacelle
- `lss`: Defines the low-speed shaft
- `hss`: Defines the high-speed shaft, when present
- `gearbox`: Defines the gearbox, when present
- `generator`: Defines the generator
- `nose`: Defines the nose
- `bedplate`: Defines the bedplate
- `other_components`: Defines the auxiliary components of the nacelle
- `elastic_properties`: Defines the equivalent elastic properties of the nacelle

Users should refer to the :doc:`detailed_turbine_documentation` for the details of each subfield. The drivetrain of the IEA-15MW turbine is defined as shown below. Note that many inputs are optional and currently only used by NREL's systems engineering tool WISDEM, which was used to design the IEA-15MW turbine.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 439-542

Yaw
~~~
The `yaw` section of the turbine YAML file provides detailed specifications for the wind turbine yaw system. Currently it only includes the equivalent `elastic_properties` of the yaw system. The yaw system of the IEA-15MW turbine is defined as shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 543-547

Tower
~~~~~
The `tower` section of the turbine YAML file provides detailed specifications for the wind turbine tower. It includes the following subfields:
- `reference_axis`: Defines the reference axis of the tower in the tower base coordinate system. This axis is used as the basis for defining both the tower geometry and structural properties.
- `outer_shape`: Defines the outer shape of the tower
- `structure`: Defines the inner structure of the tower
- `elastic_properties`: Defines the equivalent elastic properties of the tower

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 548-573

Monopile
~~~~~~~~
The `monopile` section of the turbine YAML file provides detailed specifications for the wind turbine monopile, when present. It includes the following subfields:
- `reference_axis`: Defines the reference axis of the monopile in the tower base coordinate system. This axis is used as the basis for defining both the monopile geometry and structural properties.
- `outer_shape`: Defines the outer shape of the monopile
- `structure`: Defines the inner structure of the monopile
- `elastic_properties`: Defines the equivalent elastic properties of the monopile

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 574-602

Floating platform
~~~~~~~~~~~~~~~~~
The `floating_platform` section of the turbine YAML file provides detailed specifications for the wind turbine floating platform, when present. It includes the following subfields:
- `transition_piece_mass`
- `transition_piece_cost`
- `joints`
- `members`

The floating platform of the IEA-15MW turbine is defined as shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT_VolturnUS-S.yaml
    :language: yaml
    :lines: 574-766

Users should refer to the :doc:`detailed_turbine_documentation` for the details of each subfield.

Mooring
~~~~~~~
The `mooring` section of the turbine YAML file provides detailed specifications for the floating wind turbine mooring system, when present. It includes the following subfields:
- `nodes`: Defines the nodes of the mooring system
- `lines`: Defines the lines of the mooring system
- `line_types`: Defines the characteristics of the lines
- `anchor_types`: Defines the characteristics of the anchors

The floating platform of the IEA-15MW turbine is defined as shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT_VolturnUS-S.yaml
    :language: yaml
    :lines: 767-819

Users should refer to the :doc:`detailed_turbine_documentation` for the details of each subfield.

Airfoils
---------------
The `airfoils` section of the turbine YAML file provides a database of airfoil coordinates, polars, and unsteady aero parameters. Each aifoil includes the following subfields:
- `coordinates`: Defines the coordinates of the airfoils
- `aerodynamic_center`: Defines the chordwise position of aerodynamic center of the airfoils
- `rthick`: Defines the relative thickness of the airfoils
- `polars`: Defines the polars of the airfoils

Multiple sets of `polars` can be defined for each airfoil at varying conditions, for example distinguishing wind tunnel conditions and numerical results, or different roughness conditions. Also, for each configuration, multiple sets of polars can be defined at varying Reynolds number. Note that for every set of polars the user can opt to specify the unsteady parameters often required by aeroelastic models.

An example of the `FFA-W3-211` airfoil used in the IEA-15MW turbine is shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 642-661

Note that in this example only one configuration of polars at a single Re number is defined. The user can define multiple configurations by adding more entries to the `polars` field. The `polars` field is a list of dictionaries, where each dictionary represents a different configuration of polars. Multiple sets of polars for the same configuration under different Re numbers can be defined by adding more entries to the `re_sets` field. The `re_sets` field is a second list of dictionaries, where each dictionary represents polars at varying Reynolds.

Materials
---------

The `materials` section of the turbine YAML file provides detailed specifications for the materials used in the wind turbine. The details of each entry are discussed in the page :doc:`detailed_turbine_documentation`. An example of the material `glass_biax` used in the IEA-15MW turbine is shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 878-901

Control
-------
The `control` section of the turbine YAML file provides detailed specifications for the wind turbine control system. It includes the following subfields:
- `supervisory`: Defines the parameters of the supervisory control system
- `pitch`: Defines the parameters of the pitch control system
- `torque`: Defines the parameters of the torque control system
- `yaw`: Defines the parameters of the yaw control system

The details of each field are discussed in the page :doc:`detailed_turbine_documentation`. An example of the `control` section of the IEA-15MW turbine is shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 970-984

Environment
-----------
The `environment` section of the turbine YAML file provides detailed specifications for the environmental conditions and parameters faced by the wind turbine. The details of each field are discussed in the page :doc:`detailed_turbine_documentation`. An example of the `environment` section of the IEA-15MW turbine is shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 985-997

Balance of System (BoS)
-----------------------
The `bos` section of the turbine YAML file provides detailed specifications for the balance of system inputs. The details of each field are discussed in the page :doc:`detailed_turbine_documentation`. An example of the `bos` section of the IEA-15MW turbine is shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 998-1014

Costs
-----
The `costs` section of the turbine YAML file provides detailed specifications for the capital and operational expenditures of the wind turbine. The details of each field are discussed in the page :doc:`detailed_turbine_documentation`. An example of the `costs` section of the IEA-15MW turbine is shown below.

.. literalinclude:: ../../../examples/turbine/IEA-15-240-RWT.yaml
    :language: yaml
    :lines: 1015-1042