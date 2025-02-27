import os
from copy import deepcopy
import numpy as np
import windIO


class v1p0_to_v2p0:
    def __init__(self, filename_v1p0, filename_v2p0, **kwargs) -> None:
        self.filename_v1p0 = filename_v1p0
        self.filename_v2p0 = filename_v2p0

    def convert(self):
        # Read the input yaml
        dict_v1p0 = windIO.load_yaml(self.filename_v1p0)
        
        # Copy the input windio dict
        dict_v2p0 = deepcopy(dict_v1p0)

        # Add windIO version
        dict_v2p0["windIO_version"] = "2.0"
        
        # Switch from pitch_axis to section_offset_x
        # First interpolate on chord grid
        blade_bem = dict_v1p0["components"]["blade"]["outer_shape_bem"]
        pitch_axis_grid =  blade_bem["pitch_axis"]["grid"]
        pitch_axis_values =  blade_bem["pitch_axis"]["values"]
        chord_grid =  blade_bem["chord"]["grid"]
        chord_values =  blade_bem["chord"]["values"]
        section_offset_x_grid = chord_grid
        pitch_axis_interp = np.interp(section_offset_x_grid,
                                      pitch_axis_grid,
                                      pitch_axis_values,
                                      )
        # Now dimensionalize offset using chord
        section_offset_x_values = pitch_axis_interp * chord_values
        dict_v2p0["components"]["blade"]["outer_shape_bem"].pop("pitch_axis")
        dict_v2p0["components"]["blade"]["outer_shape_bem"]["section_offset_x"] = {}
        dict_v2p0["components"]["blade"]["outer_shape_bem"]["section_offset_x"]["grid"] = section_offset_x_grid
        dict_v2p0["components"]["blade"]["outer_shape_bem"]["section_offset_x"]["values"] = section_offset_x_values
        
        # Convert twist from rad to deg
        twist_rad = dict_v2p0["components"]["blade"]["outer_shape_bem"]["twist"]["values"]
        dict_v2p0["components"]["blade"]["outer_shape_bem"]["twist"]["values"] = np.rad2deg(twist_rad)

        # Convert field `rotation` from rad to deg when defined in webs/layers
        # Also, switch label offset_y_pa to offset_y_ref_axis
        blade_struct = dict_v2p0["components"]["blade"]["internal_structure_2d_fem"]
        for iweb in range(len(blade_struct["webs"])):
            if "rotation" in blade_struct["webs"][iweb]:
                rotation_rad = blade_struct["webs"][iweb]["rotation"]["values"]
                blade_struct["webs"][iweb]["rotation"]["values"] = np.rad2deg(rotation_rad)
            if "offset_y_pa" in blade_struct["webs"][iweb]:
                blade_struct["webs"][iweb]["offset_y_ref_axis"] = blade_struct["webs"][iweb]["offset_y_pa"]
                blade_struct["webs"][iweb].pop("offset_y_pa")
        for ilayer in range(len(blade_struct["layers"])):
            if "rotation" in blade_struct["layers"][ilayer]:
                rotation_rad = blade_struct["layers"][ilayer]["rotation"]["values"]
                blade_struct["layers"][ilayer]["rotation"]["values"] = np.rad2deg(rotation_rad)
            if "offset_y_pa" in blade_struct["layers"][ilayer]:
                blade_struct["layers"][ilayer]["offset_y_ref_axis"] = blade_struct["layers"][ilayer]["offset_y_pa"]
                blade_struct["layers"][ilayer].pop("offset_y_pa")
        
        
        # Redefine stiffness and inertia matrices listing each element individually as opposed to an array
        if "six_x_six" in dict_v2p0["components"]["blade"]["elastic_properties_mb"]:
            blade_beam = dict_v2p0["components"]["blade"]["elastic_properties_mb"]["six_x_six"]

            # # Start by moving structural twist from rad to deg
            # if "values" in blade_beam["twist"]:
            #     twist_rad = blade_beam["twist"]["values"]
            #     blade_beam["twist"]["values"] = np.rad2deg(twist_rad)

            # # Move reference_axis up to level
            # blade_beam["reference_axis"] = blade_beam["reference_axis"]

            # Now open up stiffness matrix, listing each Kij entry
            blade_beam["stiffness_matrix"] = {}
            blade_beam["stiffness_matrix"]["grid"] = blade_beam["stiff_matrix"]["grid"]
            Kij = ["K11","K12","K13","K14","K15","K16",
                   "K22","K23","K24","K25","K26",
                   "K33","K34","K35","K36",
                   "K44","K45","K46",
                   "K55","K56",
                   "K66",
                   ]
            n_grid = len(blade_beam["stiffness_matrix"]["grid"])
            for ij in range(21):
                    blade_beam["stiffness_matrix"][Kij[ij]] = np.zeros(n_grid)
            for igrid in range(n_grid):
                Kval = blade_beam["stiff_matrix"]["values"][igrid]
                for ij in range(21):
                    blade_beam["stiffness_matrix"][Kij[ij]][igrid] = Kval[ij]

            # Pop out old stiff_matrix field
            blade_beam.pop("stiff_matrix")
            
            # Move on to inertia matrix
            I = blade_beam["inertia_matrix"]
            I["mass"] = np.zeros(n_grid)
            I["cm_x"] = np.zeros(n_grid)
            I["cm_y"] = np.zeros(n_grid)
            I["i_edge"] = np.zeros(n_grid)
            I["i_flap"] = np.zeros(n_grid)
            I["i_plr"] = np.zeros(n_grid)
            I["i_cp"] = np.zeros(n_grid)
            for igrid in range(n_grid):
                I["mass"][igrid] = I["values"][igrid][0]
                I["cm_x"][igrid] = I["values"][igrid][10]/I["values"][igrid][0]
                I["cm_y"][igrid] = -I["values"][igrid][5]/I["values"][igrid][0]
                I["i_edge"][igrid] = I["values"][igrid][15]
                I["i_flap"][igrid] = I["values"][igrid][18]
                I["i_plr"][igrid] = I["values"][igrid][20]
                I["i_cp"][igrid] = -I["values"][igrid][16]
            
            I.pop("values")

            # Add required field structural damping
            blade_beam["structural_damping"] = {}
            blade_beam["structural_damping"]["mu"] = np.zeros(6)

            dict_v2p0["components"]["blade"]["elastic_properties_mb"] = blade_beam

        # Cone angle from rad to deg
        cone_rad = dict_v2p0["components"]["hub"]["cone_angle"]
        dict_v2p0["components"]["hub"]["cone_angle"] = np.rad2deg(cone_rad)

        # Hub drag coefficient to cd
        dict_v2p0["components"]["hub"]["cd"] = dict_v2p0["components"]["hub"]["drag_coefficient"]
        dict_v2p0["components"]["hub"].pop("drag_coefficient")

        # Split nacelle components
        v1p0_dt = deepcopy(dict_v2p0["components"]["nacelle"]["drivetrain"])
        dict_v2p0["components"]["drivetrain"] = {}
        dict_v2p0["components"]["drivetrain"]["outer_shape_bem"] = {}
        if "uptilt" in v1p0_dt:
            uptilt_rad = v1p0_dt["uptilt"]
            dict_v2p0["components"]["drivetrain"]["outer_shape_bem"]["uptilt"] = np.rad2deg(uptilt_rad)
        if "distance_tt_hub" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape_bem"]["distance_tt_hub"] = v1p0_dt["distance_tt_hub"]
        if "distance_hub2mb" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape_bem"]["distance_hub_mb"] = v1p0_dt["distance_hub2mb"]
        if "distance_mb2mb" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape_bem"]["distance_mb_mb"] = v1p0_dt["distance_mb2mb"]
        if "overhang" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape_bem"]["overhang"] = v1p0_dt["overhang"]
        if "drag_coefficient" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape_bem"]["cd"] = v1p0_dt["drag_coefficient"]
        
        dict_v2p0["components"]["drivetrain"]["gearbox"] = {}
        if "gear_ratio" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["gear_ratio"] =  v1p0_dt["gear_ratio"]
        if "length_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["length_user"] = v1p0_dt["length_user"]
        if "radius_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["radius_user"] = v1p0_dt["radius_user"]
        if "mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["mass_user"] = v1p0_dt["mass_user"]
        if "gearbox_efficiency" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["efficiency"] = v1p0_dt["gearbox_efficiency"]
        if "damping_ratio" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["damping_ratio"] = v1p0_dt["damping_ratio"]
        if "gear_configuration" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["gear_configuration"] = v1p0_dt["gear_configuration"]
        if "planet_numbers" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["planet_numbers"] = v1p0_dt["planet_numbers"]
        
        dict_v2p0["components"]["drivetrain"]["lss"] = {}
        if "lss_length" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["lss"]["length"] = v1p0_dt["lss_length"]
        if "lss_diameter" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["lss"]["diameter"] = v1p0_dt["lss_diameter"]
        if "lss_wall_thickness" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["lss"]["wall_thickness"] = v1p0_dt["lss_wall_thickness"]
        if "lss_material" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["lss"]["material"] = v1p0_dt["lss_material"]
        
        dict_v2p0["components"]["drivetrain"]["hss"] = {}
        if "hss_length" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["hss"]["length"] = v1p0_dt["hss_length"]
        if "hss_diameter" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["hss"]["diameter"] = v1p0_dt["hss_diameter"]
        if "hss_wall_thickness" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["hss"]["wall_thickness"] = v1p0_dt["hss_wall_thickness"]
        if "hss_material" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["hss"]["material"] = v1p0_dt["hss_material"]
        
        dict_v2p0["components"]["drivetrain"]["nose"] = {}
        if "nose_diameter" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["nose"]["diameter"] = v1p0_dt["nose_diameter"]
        if "nose_wall_thickness" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["nose"]["wall_thickness"] = v1p0_dt["nose_wall_thickness"]
        
        dict_v2p0["components"]["drivetrain"]["bedplate"] = {}
        if "bedplate_wall_thickness" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["bedplate"]["wall_thickness"] = v1p0_dt["bedplate_wall_thickness"]
        if "bedplate_flange_width" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["bedplate"]["flange_width"] = v1p0_dt["bedplate_flange_width"]
        if "bedplate_flange_thickness" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["bedplate"]["flange_thickness"] = v1p0_dt["bedplate_flange_thickness"]
        if "bedplate_web_thickness" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["bedplate"]["web_thickness"] = v1p0_dt["bedplate_web_thickness"]
        if "bedplate_material" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["bedplate"]["material"] = v1p0_dt["bedplate_material"]
        
        dict_v2p0["components"]["drivetrain"]["other_components"] = {}
        if "brake_mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["brake_mass_user"] = v1p0_dt["brake_mass_user"]
        if "hvac_mass_coefficient" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["hvac_mass_coefficient"] = v1p0_dt["hvac_mass_coefficient"]
        if "converter_mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["converter_mass_user"] = v1p0_dt["converter_mass_user"]
        if "transformer_mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["transformer_mass_user"] = v1p0_dt["transformer_mass_user"]
        if "mb1Type" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["mb1Type"] = v1p0_dt["mb1Type"]
        if "mb2Type" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["mb2Type"] = v1p0_dt["mb2Type"]
        if "uptower" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["uptower"] = v1p0_dt["uptower"]
        
        dict_v2p0["components"]["drivetrain"]["generator"] = deepcopy(dict_v2p0["components"]["nacelle"]["generator"])
        if "generator_length" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["generator"]["length"] = v1p0_dt["generator_length"]
        if "generator_radius_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["generator"]["radius"] = v1p0_dt["generator_radius_user"]
        if "generator_mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["generator"]["mass"] = v1p0_dt["generator_mass_user"]
        if "rpm_efficiency_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["generator"]["rpm_efficiency"] = v1p0_dt["rpm_efficiency_user"]
        v1p0_gen = deepcopy(dict_v2p0["components"]["nacelle"]["generator"])
        if "generator_type" in v1p0_gen:
            dict_v2p0["components"]["drivetrain"]["generator"]["type"] = v1p0_gen["generator_type"]
            dict_v2p0["components"]["drivetrain"]["generator"].pop("generator_type")

        if "phi" in dict_v2p0["components"]["drivetrain"]["generator"]:
            phi_rad = dict_v2p0["components"]["drivetrain"]["generator"]["phi"]
            dict_v2p0["components"]["drivetrain"]["generator"]["phi"] = np.rad2deg(phi_rad)

        dict_v2p0["components"].pop("nacelle")

        # Tower and monopile drag_coefficient renamed cd
        cd_tower = dict_v2p0["components"]["tower"]["outer_shape_bem"]["drag_coefficient"]
        dict_v2p0["components"]["tower"]["outer_shape_bem"]["cd"] = cd_tower
        dict_v2p0["components"]["tower"]["outer_shape_bem"].pop("drag_coefficient")
        
        if "monopile" in dict_v2p0["components"]:
            cd_monopile = dict_v2p0["components"]["monopile"]["outer_shape_bem"]["drag_coefficient"]
            dict_v2p0["components"]["monopile"]["outer_shape_bem"]["cd"] = cd_monopile
            dict_v2p0["components"]["monopile"]["outer_shape_bem"].pop("drag_coefficient")

        # Rad to deg in some inputs to floating platform
        if "floating_platform" in dict_v2p0["components"]:
            members = dict_v2p0["components"]["floating_platform"]["members"]
            for i_memb in range(len(members)):
                members[i_memb]["ca"] = members[i_memb]["Ca"]
                members[i_memb].pop("Ca")
                members[i_memb]["cd"] = members[i_memb]["Cd"]
                members[i_memb].pop("Cd")
                if "angles" in members[i_memb]["outer_shape"]:
                    angles_rad = members[i_memb]["outer_shape"]["angles"]
                    members[i_memb]["outer_shape"]["angles"] = np.rad2deg(angles_rad)
                if "rotation" in members[i_memb]["outer_shape"]:
                    rotation_rad = members[i_memb]["outer_shape"]["rotation"]
                    members[i_memb]["outer_shape"]["rotation"] = np.rad2deg(rotation_rad)
                if "ring_stiffeners" in members[i_memb]["internal_structure"]:
                    if "spacing" in members[i_memb]["internal_structure"]["ring_stiffeners"]:
                        spacing_rad = members[i_memb]["internal_structure"]["ring_stiffeners"]["spacing"]
                        members[i_memb]["internal_structure"]["ring_stiffeners"]["spacing"] = np.rad2deg(spacing_rad)

        # Airfoils: angle of attack in deg and cl, cd, cm tags
        for i_af in range(len(dict_v2p0["airfoils"])):
            af = dict_v2p0["airfoils"][i_af]
            for i_plr in range(len(af["polars"])):
                plr = af["polars"][i_plr]
                plr["cl"] = {}
                aoa_rad = deepcopy(plr["c_l"]["grid"])
                plr["cl"]["grid"] = np.rad2deg(aoa_rad)
                plr["cl"]["grid"][0] = -180
                plr["cl"]["grid"][-1] = 180
                plr["cl"]["values"] = deepcopy(plr["c_l"]["values"])
                plr.pop("c_l")

                plr["cd"] = {}
                aoa_rad = deepcopy(plr["c_d"]["grid"])
                plr["cd"]["grid"] = np.rad2deg(aoa_rad)
                plr["cd"]["grid"][0] = -180
                plr["cd"]["grid"][-1] = 180
                plr["cd"]["values"] = deepcopy(plr["c_d"]["values"])
                plr.pop("c_d")

                plr["cm"] = {}
                aoa_rad = deepcopy(plr["c_m"]["grid"])
                plr["cm"]["grid"] = np.rad2deg(aoa_rad)
                plr["cm"]["grid"][0] = -180
                plr["cm"]["grid"][-1] = 180
                plr["cm"]["values"] = deepcopy(plr["c_m"]["values"])
                plr.pop("c_m")

        # Materials
        # manufacturing_id instead of component_id
        for i_mat in range(len(dict_v2p0["materials"])):
            if "component_id" in dict_v2p0["materials"][i_mat]:
                dict_v2p0["materials"][i_mat]["manufacturing_id"] = dict_v2p0["materials"][i_mat]["component_id"]
                dict_v2p0["materials"][i_mat].pop("component_id")
            if "alp0" in dict_v2p0["materials"][i_mat]:
                alp0_rad = dict_v2p0["materials"][i_mat]["alp0"]
                if alp0_rad < np.pi:
                    dict_v2p0["materials"][i_mat]["alp0"] = np.rad2deg(alp0_rad)

        # Controls, update a few fields from rad to deg and from rad/s to rpm
        min_pitch_rad = dict_v2p0["control"]["pitch"]["min_pitch"]
        dict_v2p0["control"]["pitch"]["min_pitch"] = np.rad2deg(min_pitch_rad)
        max_pitch_rad = dict_v2p0["control"]["pitch"]["max_pitch"]
        dict_v2p0["control"]["pitch"]["max_pitch"] = np.rad2deg(max_pitch_rad)
        max_pitch_rate_rad = dict_v2p0["control"]["pitch"]["max_pitch_rate"]
        dict_v2p0["control"]["pitch"]["max_pitch_rate"] = np.rad2deg(max_pitch_rate_rad)
        VS_minspd_rads = dict_v2p0["control"]["torque"]["VS_minspd"]
        dict_v2p0["control"]["torque"]["VS_minspd"] = VS_minspd_rads * 30. / np.pi
        VS_maxspd_rads = dict_v2p0["control"]["torque"]["VS_maxspd"]
        dict_v2p0["control"]["torque"]["VS_maxspd"] = VS_maxspd_rads * 30. / np.pi
        if "PC_zeta" in dict_v2p0["control"]["pitch"]:
            dict_v2p0["control"]["pitch"].pop("PC_zeta")
        if "PC_omega" in dict_v2p0["control"]["pitch"]:
            dict_v2p0["control"]["pitch"].pop("PC_omega")
        if "VS_zeta" in dict_v2p0["control"]["torque"]:
            dict_v2p0["control"]["torque"].pop("VS_zeta")
        if "VS_omega" in dict_v2p0["control"]["torque"]:
            dict_v2p0["control"]["torque"].pop("VS_omega")
        if "control_type" in dict_v2p0["control"]["torque"]:
            dict_v2p0["control"]["torque"].pop("control_type")
        if "setpoint_smooth" in dict_v2p0["control"]:
            dict_v2p0["control"].pop("setpoint_smooth")
        if "shutdown" in dict_v2p0["control"]:
            dict_v2p0["control"].pop("shutdown")


        # Print out
        windIO.write_yaml(dict_v2p0, self.filename_v2p0)


if __name__ == "__main__":
    
    filename_v1p0 = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        "v1p0",
                        "IEA-15-240-RWT.yaml"
                    )
    
    filename_v2p0 = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "v2p0",
                    "IEA-15-240-RWT.yaml"
                )
    
    converter = v1p0_to_v2p0(filename_v1p0, filename_v2p0)
    converter.convert()
    
    filename_v1p0 = os.path.join(
                        os.path.dirname(os.path.realpath(__file__)),
                        "v1p0",
                        "IEA-15-240-RWT_VolturnUS-S.yaml"
                    )
    
    filename_v2p0 = os.path.join(
                    os.path.dirname(os.path.realpath(__file__)),
                    "v2p0",
                    "IEA-15-240-RWT_VolturnUS-S.yaml"
                )
    
    converter = v1p0_to_v2p0(filename_v1p0, filename_v2p0)
    converter.convert()