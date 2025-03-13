Materials
------------

**NOTE windIO has moved!** The windIO source code repository and documentation have moved to the following locations:

- Documentation is hosted at https://ieawindsystems.github.io/windio
- Source code repository is now https://github.com/ieawindsystems/windio

----

windIO defines a material database, which consists of a list of entries each marked by a dash. 

.. literalinclude:: ../../test/turbine_example.yaml
    :start-after: # Materials
    :end-before: # Assembly

:code:`name` : String
    Name of the material
:code:`description` : String
    Optional string to describe the material
:code:`source` : String
    Optional string to describe the origin of the material, for example referencing a report or a paper
:code:`orth` : Boolean
    Flag specifying whether a material is isotropic (0) or orthotropic (1). This determines whether some of the fields below are specified as a float or an array of floats.
:code:`rho` : Float, kg/m3
    Density of the material. For composites, this is the density of the laminate once cured.
:code:`E` : Float (:code:`orth=0`), array of three floats (:code:`orth=1`), Pa
    Stiffness modulus. For orthotropic materials, it consists of an array with E11, E22, and E33 (see below about the reference system).
:code:`G` : Float (:code:`orth=0`), array of three floats (:code:`orth=1`), Pa
    Shear stiffness modulus. For orthotropic materials, it consists of an array with G12, G13, and G23.
:code:`nu` : Float (:code:`orth=0`), array of three floats (:code:`orth=1`)
    Poisson ratio. For orthotropic materials, it consists of an array with nu12, nu13, and nu23.
:code:`Xt` : Float (:code:`orth=0`), array of three floats (:code:`orth=1`), Pa
    Ultimate tensile strength. For orthotropic materials, it consists of an array with Xt11, Xt22, and Xt33.
:code:`Xc` : Float (:code:`orth=0`), array of three floats (:code:`orth=1`), Pa
    Ultimate compressive strength. For orthotropic materials, it consists of an array with Xc11, Xc22, and Xc33. Values are defined positive.
:code:`Xy` : Float, Pa
    Ultimate yield strength.
:code:`S` : Float (:code:`orth=0`), array of three floats (:code:`orth=1`), Pa
    Ultimate shear strength. For orthotropic materials, it consists of an array with S12, S13, and S23. Values are defined positive.
:code:`alpha` : Float (:code:`orth=0`) or array of three floats (:code:`orth=1`), 1/K 
    Thermal coefficient of expansion. For orthotropic materials, it consists of an array with alpha11, alpha22, and alpha33.
:code:`GIc` : Float, J/m2
     Mode 1 critical energy-release rate.
:code:`GIIc` : Float, J/m2
    Mode 2 critical energy-release rate.
:code:`alp0` : Float, rad
    Fracture angle under pure transverse compression.
:code:`fvf` : Float
    Fiber volume fraction of a composite material. The minimum values is 0 (only matrix), the maximum value is 1 (only fibers).
:code:`fwf` : Float
    Fiber weight fraction of a composite material. The minimum values is 0 (only matrix), the maximum value is 1 (only fibers).
:code:`ply_t` : Float 
    Ply thickness of a composite material. The unit of measure is m. The actual laminate thickness is defined in the fields :code:`components`.
:code:`unit_cost` : Float, $/kg
    Unit cost of the material. For composites, this is the unit cost of the dry fabric.
:code:`fiber_density` : Float, kg/m3
    Density of the fibers of a composite material. Standard glass fiber has a fiber density of approximately 2600 kg/m3, while standard carbon fiber has a fiber density of approximately 1800 kg/m3.
:code:`A` : Float (:code:`orth=0`) or array of three floats (:code:`orth=1`) 
    Fatigue S/N curve fitting parameter S=A*N^(-1/m).
:code:`m` : Float (:code:`orth=0`) or array of three floats (:code:`orth=1`) 
    Fatigue S/N curve fitting parameter S=A*N^(-1/m).
:code:`R` : Float (:code:`orth=0`) or array of three floats (:code:`orth=1`) 
    Fatigue stress ratio.
:code:`area_density_dry` : Float, kg/m2 
    Aerial density of the fabric of a composite material.
:code:`waste` : Float
    Fraction of material that ends up wasted during manufacturing. This quantity is used in the NREL blade cost model https://www.nrel.gov/docs/fy19osti/73585.pdf.
:code:`roll_mass` : Float, kg
    Mass of a roll of fabric. This quantity is used in the NREL blade cost model https://www.nrel.gov/docs/fy19osti/73585.pdf.
:code:`component_id` : Integer
    Flag to define the manufacturing process behind a laminates. It is used by the NREL blade cost model https://www.nrel.gov/docs/fy19osti/73585.pdf . 0 - coating, 1 - sandwich filler , 2 - shell skin, 3 - shear webs, 4 - spar caps, 5 - TE reinf.

The schema enforces that the fields :code:`name`, :code:`orth`, :code:`rho`, :code:`E`, and :code:`nu` are specified.

For composites, direction 1 is aligned with the main fiber direction, direction 2 is in the plane transverse to the fibers, and direction 3 is perspendicular to the laminate plane. Note that fiber angles are specified in :code:`internal_structure_2d_fem`.


