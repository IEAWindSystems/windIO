import os
import traceback
from copy import deepcopy
import numpy as np
import windIO


class v1p0_to_v2p0:
    def __init__(self, filename_v1p0, filename_v2p0, **kwargs) -> None:
        self.filename_v1p0 = filename_v1p0
        self.filename_v2p0 = filename_v2p0

    def convert(self):
        print("Converter windIO v1.0 to v2.0 started.")

        print("Load file %s:"%self.filename_v1p0)

        # Read the input yaml
        dict_v1p0 = windIO.load_yaml(self.filename_v1p0)
        
        # Set windIO version
        self.dict_v2p0 = dict_v2p0 = {"windIO_version": "2.0"}

        # Copy the input windio dict
        dict_v2p0.update(deepcopy(dict_v1p0))

        if "description" in dict_v2p0:
            dict_v2p0["comments"] = dict_v2p0["description"]
            dict_v2p0.pop("description")

        try:
            dict_v2p0 = self.convert_blade(dict_v2p0)
            print("Blade converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Blade component could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        try:
            dict_v2p0 = self.convert_nacelle(dict_v2p0)
            print("Nacelle converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Nacelle component could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        try:
            dict_v2p0 = self.convert_tower(dict_v2p0)
            print("Tower converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Tower component could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        if "monopile" in dict_v2p0["components"]:
            try:
                dict_v2p0 = self.convert_monopile(dict_v2p0)
                print("Monopile converted successfully")
            except Exception as e:
                print(traceback.format_exc())
                print("⚠️ Monopile component could not be converted successfully. Please check.")
                print(f"Error details: {e}")
        if "floating_platform" in dict_v2p0["components"]:
            try:
                dict_v2p0 = self.convert_floating_platform(dict_v2p0)
                print("Floating platform converted successfully")
            except Exception as e:
                print(traceback.format_exc())
                print("⚠️ Floating platform component could not be converted successfully. Please check.")
                print(f"Error details: {e}")
        try:
            dict_v2p0 = self.convert_airfoils(dict_v2p0)
            print("Airfoil database converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Airfoil database could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        try:
            dict_v2p0 = self.convert_materials(dict_v2p0)
            print("Material database converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Material database could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        try:
            dict_v2p0 = self.convert_controls(dict_v2p0)
            print("Control block converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Control block database could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        
        # If present, remove WISDEM specific environment, bos, and costs properties from schema
        if "environment" in dict_v2p0:
            dict_v2p0.pop("environment")
        if "bos" in dict_v2p0:
            dict_v2p0.pop("bos")
        if "costs" in dict_v2p0:
            dict_v2p0.pop("costs")

        # Print out
        print("New yaml file being generated: %s"%self.filename_v2p0)
        windIO.yaml.write_yaml(dict_v2p0, self.filename_v2p0)
        
        print("Converter windIO v1.0 to v2.0 ended.")

    def convert_blade(self, dict_v2p0):
        dict_v2p0 = self.convert_blade_reference_axis(dict_v2p0)
        dict_v2p0 = self.convert_blade_outer_shape(dict_v2p0)
        dict_v2p0 = self.convert_blade_structure(dict_v2p0)
        if "elastic_properties_mb" in dict_v2p0["components"]["blade"]:
            if "six_x_six" in dict_v2p0["components"]["blade"]["elastic_properties_mb"]:
                dict_v2p0 = self.convert_elastic_properties(dict_v2p0)
        return dict_v2p0
    
    def convert_blade_reference_axis(self, dict_v2p0):
        
        # New common ref axis for all blade subfields, take the aero shape one by default
        dict_v2p0["components"]["blade"]["reference_axis"] = deepcopy(dict_v2p0["components"]["blade"]["outer_shape_bem"]["reference_axis"])
        dict_v2p0["components"]["blade"]["outer_shape_bem"].pop("reference_axis")

        return dict_v2p0
    
    def convert_blade_outer_shape(self, dict_v2p0):
        # Start by changing name
        dict_v2p0["components"]["blade"]["outer_shape"] = dict_v2p0["components"]["blade"]["outer_shape_bem"]
        dict_v2p0["components"]["blade"].pop("outer_shape_bem")
        
        # Switch from pitch_axis to section_offset_x
        # First interpolate on chord grid
        blade_os = dict_v2p0["components"]["blade"]["outer_shape"]
        pitch_axis_grid =  blade_os["pitch_axis"]["grid"]
        pitch_axis_values =  blade_os["pitch_axis"]["values"]
        chord_grid =  blade_os["chord"]["grid"]
        chord_values =  blade_os["chord"]["values"]
        section_offset_x_grid = chord_grid
        pitch_axis_interp = np.interp(section_offset_x_grid,
                                      pitch_axis_grid,
                                      pitch_axis_values,
                                      )
        # Now dimensionalize offset using chord
        section_offset_x_values = pitch_axis_interp * chord_values
        blade_os.pop("pitch_axis")
        blade_os["section_offset_x"] = {}
        blade_os["section_offset_x"]["grid"] = section_offset_x_grid
        blade_os["section_offset_x"]["values"] = section_offset_x_values
        
        # Convert twist from rad to deg
        twist_rad = blade_os["twist"]["values"]
        blade_os["twist"]["values"] = np.rad2deg(twist_rad)

        # Restructure how airfoil spanwise positions are defined
        n_af = len(blade_os["airfoil_position"]["grid"])
        blade_os["airfoils"] = [{}]
        for i in range(n_af):
            if i>0:
                blade_os["airfoils"].append({})
            blade_os["airfoils"][i]["name"] = blade_os["airfoil_position"]["labels"][i]
            blade_os["airfoils"][i]["spanwise_position"] = blade_os["airfoil_position"]["grid"][i]
            blade_os["airfoils"][i]["configuration"] = ["default"]
            blade_os["airfoils"][i]["weight"] = [1.]


        if "rthick" not in blade_os:
            rthick_v1p0 = np.zeros(n_af)            
            n_af_available = len(dict_v2p0["airfoils"])
            for i in range(n_af):
                for j in range(n_af_available):
                    if blade_os["airfoil_position"]["labels"][i] == dict_v2p0["airfoils"][j]["name"]:
                        rthick_v1p0[i] = dict_v2p0["airfoils"][j]["relative_thickness"]
            # Use numpy polyfit
            coeffs = np.polyfit(blade_os["airfoil_position"]["grid"], rthick_v1p0, deg=3)
            poly = np.poly1d(coeffs)
            rthick = poly(chord_grid)
            rthick[rthick>1.]=1.
            blade_os["rthick"] = {}
            blade_os["rthick"]["grid"] = chord_grid
            blade_os["rthick"]["values"] = rthick

        blade_os.pop("airfoil_position")

        return dict_v2p0
    
    def convert_blade_structure(self, dict_v2p0):
        # Start by changing name
        dict_v2p0["components"]["blade"]["structure"] = dict_v2p0["components"]["blade"]["internal_structure_2d_fem"]
        dict_v2p0["components"]["blade"].pop("internal_structure_2d_fem")
        # Convert field `rotation` from rad to deg when defined in webs/layers
        # Also, switch label offset_y_pa to offset_y_reference_axis
        blade_struct = dict_v2p0["components"]["blade"]["structure"]
        layers_v1p0 = deepcopy(dict_v2p0["components"]["blade"]["structure"]["layers"])
        webs_v1p0 = deepcopy(dict_v2p0["components"]["blade"]["structure"]["webs"])

        # construct new sub-sections
        blade_struct["anchors"] = []
        te_anchor = {"name": "TE",
                     "start_nd_arc": {
                         "grid": [0., 1.],
                         "values": [0.0, 0.0]
                        },
                     "end_nd_arc": {
                         "grid": [0., 1.],
                         "values": [1.0, 1.0]
                        }
                     }
        le_anchor = {"name": "LE",
                     "start_nd_arc": {
                         "grid": [0., 1.],
                         "values": [0.5, 0.5]
                        },
                     }
        blade_struct["anchors"].append(te_anchor)
        blade_struct["anchors"].append(le_anchor)
        print("Warning: Adding LE anchor with dummy values, update manually!")
        blade_struct["webs"] = []
        blade_struct["layers"] = []

        def convert_arcs(layer_v1p0, anchors, is_web=False):

            anchor_names = [a["name"] for a in anchors]

            name = layer_v1p0["name"]
            layer = {}
            anchor = None
            start_anchor_name = "not_defined"
            start_anchor_handle = "not_defined"
            end_anchor_name = "not_defined"
            end_anchor_handle = "not_defined"
            start_fixed = None
            end_fixed = None

            layer["name"] = name
            if is_web:
                if "start_nd_arc" in layer_v1p0:
                    layer["start_nd_grid"] = layer_v1p0["start_nd_arc"]["grid"][0]
                    layer["end_nd_grid"] = layer_v1p0["start_nd_arc"]["grid"][-1]
                elif "offset_y_pa" in layer_v1p0:
                    layer["start_nd_grid"] = layer_v1p0["offset_y_pa"]["grid"][0]
                    layer["end_nd_grid"] = layer_v1p0["offset_y_pa"]["grid"][-1]
                else:
                    print(f"⚠️ Field start_nd_arc or offset_y_pa not found for {name}. Using dummy values for start_nd_grid.")
                    layer["start_nd_grid"] = 0.0
                    layer["end_nd_grid"] = 1.0
            else:
                layer["start_nd_grid"] = layer_v1p0["thickness"]["grid"][0]
                layer["end_nd_grid"] = layer_v1p0["thickness"]["grid"][-1]

            zeros_dict = {"grid": [layer["start_nd_grid"], layer["end_nd_grid"]],
                          "values": [0.0, 0.0]}
            ones_dict = {"grid": [layer["start_nd_grid"], layer["end_nd_grid"]],
                          "values": [1.0, 1.0]}
            dummy_dict = {"grid": "N/A",
                          "values": "N/A"}
            # move definition of start_nd_arc and end_nd_arc to anchors
            if "start_nd_arc" in layer_v1p0:
                if "fixed" in layer_v1p0["start_nd_arc"]:
                    start_fixed = layer_v1p0["start_nd_arc"]["fixed"]
                    # we don't construct a new anchor but reference an existing one
                    start_anchor_name = layer_v1p0["start_nd_arc"]["fixed"]
                    if start_fixed == "TE":
                        start_anchor_handle = "start_nd_arc"
                    else:
                        start_anchor_handle = "end_nd_arc"
                else:
                    if anchor is None:
                        anchor = {}
                    anchor["name"] = name
                    anchor["start_nd_arc"] = layer_v1p0["start_nd_arc"]
                    start_anchor_name = layer_v1p0["name"]
                    start_anchor_handle = "start_nd_arc"
            if "end_nd_arc" in layer_v1p0:
                if "fixed" in layer_v1p0["end_nd_arc"]:
                    # we don't construct a new anchor but reference an existing one
                    end_fixed = layer_v1p0["end_nd_arc"]["fixed"]
                    end_anchor_name = layer_v1p0["end_nd_arc"]["fixed"]
                    if end_fixed == "TE":
                        end_anchor_handle = "end_nd_arc"
                    else:
                        end_anchor_handle = "start_nd_arc"
                else:
                    try:
                        if anchor is None:
                            anchor = {}
                        anchor["name"] = name
                        anchor["end_nd_arc"] = layer_v1p0["end_nd_arc"]
                        end_anchor_name = layer_v1p0["name"]
                        end_anchor_handle = "end_nd_arc"
                    except Exception as e:
                        print(traceback.format_exc())
                        print("⚠️ Required field end_nd_arc not found for %s. Please check." % layer_v1p0["name"])
                        print(f"Error details: {e}")
            if "midpoint_nd_arc" in layer_v1p0:
                if anchor is None:
                    anchor = {}
                if "fixed" in layer_v1p0["midpoint_nd_arc"]:
                    anchor["midpoint_nd_arc"] = {}
                    anchor["midpoint_nd_arc"]["anchor"] = {"name": layer_v1p0["midpoint_nd_arc"]["fixed"],
                                                           "handle": "start_nd_arc"}
                    if layer_v1p0["midpoint_nd_arc"]["fixed"] == "LE":
                        print("⚠️ Computing LE anchor from layer %s, please check!" % layer_v1p0["name"])
                        LE = (np.array(layer_v1p0.get("end_nd_arc", {}).get("values", np.ones_like(layer_v1p0["thickness"]["grid"]))) + 
                                       layer_v1p0.get("start_nd_arc", {}).get("values", np.ones_like(layer_v1p0["thickness"]["grid"]))) / 2.0
                        LE_anchor = {"name": "LE",
                                     "start_nd_arc": {"grid": layer_v1p0.get("start_nd_arc", {}).get("grid", np.ones_like(layer_v1p0["thickness"]["grid"])),
                                                      "values": LE}
                                                      }
                        if "LE" in anchor_names:
                            anchors[anchor_names.index("LE")] = LE_anchor
                        else:
                            anchors.append(LE_anchor)

                if "width" in layer_v1p0:
                    anchor["width"] = {}
                    anchor["width"]["defines"] = ["start_nd_arc", "end_nd_arc"]
                    anchor["width"].update(layer_v1p0["width"])
                else:
                    raise ValueError("width is not defined for %s, required when midpoint_nd_arc is defined" % layer_v1p0["name"])
            if "width" in layer_v1p0:
                if anchor is None:
                    anchor = {}
                anchor["name"] = name
                anchor["width"] = {}
                anchor["width"].update(layer_v1p0["width"])
                anchor["width"]["defines"] = ["start_nd_arc", "end_nd_arc"]
                if start_fixed and end_fixed:
                    raise ValueError("entity %s cannot define fixtures and both start and end"
                                    " and also define a width" % layer_v1p0["name"])
                if start_fixed:
                    anchor["width"]["defines"] = ["end_nd_arc"]
                    anchor["start_nd_arc"] = {"anchor": {
                        "name": start_anchor_name,
                        "handle": start_anchor_handle
                    }}
                # else:
                #     anchor["start_nd_arc"] = dummy_dict
                #     print("start_nd_arc not found for %s, adding dummy values!" % name)
                if end_fixed:
                    anchor["width"]["defines"] = ["start_nd_arc"]
                    anchor["end_nd_arc"] = {"anchor": {
                        "name": end_anchor_name,
                        "handle": end_anchor_handle
                    }}
                # else:
                #     anchor["end_nd_arc"] = dummy_dict
                #     print("end_nd_arc not found for %s, adding dummy values!" % name)
                # anchor["width"] = {"anchor": {
                #     "name": end_anchor_name,
                #     "handle": end_anchor_handle
                # }}
            if "rotation" in layer_v1p0 and "offset_y_pa" in layer_v1p0:
                print("Found offset_y_pa in %s. Assuming rotation to be equal to blade twist!" % layer_v1p0["name"])
                # construct plane_intersection section with zero rotation
                isect = anchor["plane_intersection"] = {}
                if is_web:
                    isect["side"] = "both"
                    isect["defines"] = ["start_nd_arc", "end_nd_arc"]
                else:
                    isect["side"] = layer_v1p0["side"]
                    isect["defines"] = ["midpoint_nd_arc"]
                isect["plane_type1"] = {"anchor_curve": "reference_axis",
                                        "anchors_nd_grid": [0.0, 1.0],
                                        "rotation": 0.0}
                isect["offset"] = layer_v1p0["offset_y_pa"]
                
            # make cross-reference in web to the anchors
            layer.setdefault("start_nd_arc", {}).setdefault("anchor", {})
            layer["start_nd_arc"]["anchor"]["name"] = start_anchor_name
            layer["start_nd_arc"]["anchor"]["handle"] = start_anchor_handle
            layer.setdefault("end_nd_arc", {}).setdefault("anchor", {})
            layer["end_nd_arc"]["anchor"]["name"] = end_anchor_name
            layer["end_nd_arc"]["anchor"]["handle"] = end_anchor_handle

            if is_web:
                web_anchor = {}
                web_anchor["name"] = "%s_shell_attachment" % name
                web_anchor["start_nd_arc"] = zeros_dict
                web_anchor["end_nd_arc"] = ones_dict
                
                layer["anchors"] = [web_anchor]

            if "web" in layer_v1p0:
                anchor_name = layer_v1p0["web"]
                layer["web"] = layer_v1p0["web"]
                layer["start_nd_arc"]["anchor"]["name"] = anchor_name + "_shell_attachment"
                layer["start_nd_arc"]["anchor"]["handle"] = "start_nd_arc"
                layer["end_nd_arc"]["anchor"]["name"] = anchor_name + "_shell_attachment"
                layer["end_nd_arc"]["anchor"]["handle"] = "end_nd_arc"
            if not is_web:
                layer["material"] = layer_v1p0["material"]
                layer["thickness"] = layer_v1p0["thickness"]
                layer["fiber_orientation"] = layer_v1p0.get("fiber_orientation", zeros_dict)
                if "n_plies" in layer_v1p0:
                    layer["n_plies"] = layer_v1p0["n_plies"]
            if anchor is not None:
                if "start_nd_arc" not in anchor:
                    anchor["start_nd_arc"] = zeros_dict
                    print("⚠️ Required field start_nd_arc not found for %s. Adding a dummy field." % layer_v1p0["name"])
                if "end_nd_arc" not in anchor:
                    anchor["end_nd_arc"] = ones_dict
                    print("⚠️ Required field end_nd_arc not found for %s. Adding a dummy field." % layer_v1p0["name"])

            return layer, anchor
        
        for web_v1p0 in webs_v1p0:
            web, anchor = convert_arcs(web_v1p0,
                                       blade_struct["anchors"],
                                       is_web=True)
            if anchor is not None:
                blade_struct["anchors"].append(anchor)
            blade_struct["webs"].append(web)
        for layer_v1p0 in layers_v1p0:
            layer, anchor = convert_arcs(layer_v1p0,
                                         blade_struct["anchors"],
                                         is_web=False)
            if anchor is not None:
                blade_struct["anchors"].append(anchor)
            blade_struct["layers"].append(layer)
        
        # Pop older ref axis
        blade_struct.pop("reference_axis")

        return dict_v2p0

    def convert_elastic_properties(self, dict_v2p0):
        # Start by changing name
        dict_v2p0["components"]["blade"]["elastic_properties"] = dict_v2p0["components"]["blade"]["elastic_properties_mb"]
        dict_v2p0["components"]["blade"].pop("elastic_properties_mb")
        # Redefine stiffness and inertia matrices listing each element individually as opposed to an array
        dict_v2p0["components"]["blade"]["structure"]["elastic_properties"] = dict_v2p0["components"]["blade"]["elastic_properties"]["six_x_six"]
        blade_beam = dict_v2p0["components"]["blade"]["structure"]["elastic_properties"]
        dict_v2p0["components"]["blade"].pop("elastic_properties")

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

        blade_beam.pop("twist")
        # Pop older ref axis
        blade_beam.pop("reference_axis")

        
        return dict_v2p0

    def convert_nacelle(self, dict_v2p0):
        
        # Cone angle from rad to deg
        cone_rad = dict_v2p0["components"]["hub"]["cone_angle"]
        dict_v2p0["components"]["hub"]["cone_angle"] = np.rad2deg(cone_rad)

        # Hub drag coefficient to cd
        dict_v2p0["components"]["hub"]["cd"] = dict_v2p0["components"]["hub"]["drag_coefficient"]
        dict_v2p0["components"]["hub"].pop("drag_coefficient")

        # Split nacelle components
        v1p0_dt = deepcopy(dict_v2p0["components"]["nacelle"]["drivetrain"])
        v1p0_nac = deepcopy(dict_v2p0["components"]["nacelle"])
        dict_v2p0["components"]["drivetrain"] = {}
        dict_v2p0["components"]["drivetrain"]["outer_shape"] = {}
        if "uptilt" in v1p0_dt:
            uptilt_rad = v1p0_dt["uptilt"]
            dict_v2p0["components"]["drivetrain"]["outer_shape"]["uptilt"] = np.rad2deg(uptilt_rad)
        if "distance_tt_hub" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape"]["distance_tt_hub"] = v1p0_dt["distance_tt_hub"]
        if "distance_hub2mb" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape"]["distance_hub_mb"] = v1p0_dt["distance_hub2mb"]
        if "distance_mb2mb" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape"]["distance_mb_mb"] = v1p0_dt["distance_mb2mb"]
        if "overhang" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape"]["overhang"] = v1p0_dt["overhang"]
        if "drag_coefficient" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["outer_shape"]["cd"] = v1p0_dt["drag_coefficient"]
        
        dict_v2p0["components"]["drivetrain"]["gearbox"] = {}
        if "gear_ratio" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["gear_ratio"] =  v1p0_dt["gear_ratio"]
        if "length_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["length"] = v1p0_dt["length_user"]
        if "radius_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["radius"] = v1p0_dt["radius_user"]
        if "mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["gearbox"]["mass"] = v1p0_dt["mass_user"]
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
            dict_v2p0["components"]["drivetrain"]["other_components"]["brake_mass"] = v1p0_dt["brake_mass_user"]
        if "hvac_mass_coefficient" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["hvac_mass_coefficient"] = v1p0_dt["hvac_mass_coefficient"]
        if "converter_mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["converter_mass"] = v1p0_dt["converter_mass_user"]
        if "transformer_mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["transformer_mass"] = v1p0_dt["transformer_mass_user"]
        if "mb1Type" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["mb1Type"] = v1p0_dt["mb1Type"]
        if "mb2Type" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["mb2Type"] = v1p0_dt["mb2Type"]
        if "uptower" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["other_components"]["uptower"] = v1p0_dt["uptower"]
        
        if "generator" in v1p0_nac:
            dict_v2p0["components"]["drivetrain"]["generator"] = deepcopy(v1p0_nac["generator"])
            if "generator_type" in v1p0_nac["generator"]:
                dict_v2p0["components"]["drivetrain"]["generator"]["type"] = v1p0_nac["generator"]["generator_type"]
                dict_v2p0["components"]["drivetrain"]["generator"].pop("generator_type")
            if "phi" in v1p0_nac["generator"]:
                phi_rad = dict_v2p0["components"]["drivetrain"]["generator"]["phi"]
                dict_v2p0["components"]["drivetrain"]["generator"]["phi"] = np.rad2deg(phi_rad)
            if "generator_length" in v1p0_nac["generator"]:
                dict_v2p0["components"]["drivetrain"]["generator"]["length"] = v1p0_nac["generator"]["generator_length"]
                dict_v2p0["components"]["drivetrain"]["generator"].pop("generator_length")
            if "rated_rpm" in v1p0_nac["generator"]:
                dict_v2p0["components"]["drivetrain"]["generator"].pop("rated_rpm")
            if "S_Nmax" in v1p0_nac["generator"]:
                dict_v2p0["components"]["drivetrain"]["generator"].pop("S_Nmax")
        else:
            dict_v2p0["components"]["drivetrain"]["generator"] = {}
        if "generator_length" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["generator"]["length"] = v1p0_dt["generator_length"]
        if "generator_radius_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["generator"]["radius"] = v1p0_dt["generator_radius_user"]
        if "generator_mass_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["generator"]["mass"] = v1p0_dt["generator_mass_user"]
        if "rpm_efficiency_user" in v1p0_dt:
            dict_v2p0["components"]["drivetrain"]["generator"]["rpm_efficiency"] = v1p0_dt["rpm_efficiency_user"]

        dict_v2p0["components"].pop("nacelle")


        return dict_v2p0

    def convert_tower(self, dict_v2p0):
        tower = dict_v2p0["components"]["tower"]
        # Start by changing outer_shape_bem to outer_shape
        tower["outer_shape"] = tower["outer_shape_bem"]
        tower.pop("outer_shape_bem")
        # Then change internal_structure_2d_fem to structure
        tower["structure"] = tower["internal_structure_2d_fem"]
        tower.pop("internal_structure_2d_fem")
        # Now define common reference axis
        tower["reference_axis"] = deepcopy(tower["outer_shape"]["reference_axis"])
        # Pop out older ref_axis
        tower["outer_shape"].pop("reference_axis")
        tower["structure"].pop("reference_axis")
        # Rename drag_coefficient to cd
        cd_tower = tower["outer_shape"]["drag_coefficient"]
        tower["outer_shape"]["cd"] = cd_tower
        tower["outer_shape"].pop("drag_coefficient")
        return dict_v2p0

    def convert_monopile(self, dict_v2p0):
        monopile = dict_v2p0["components"]["monopile"]
        # Start by changing outer_shape_bem to outer_shape
        monopile["outer_shape"] = monopile["outer_shape_bem"]
        monopile.pop("outer_shape_bem")
        # Then change internal_structure_2d_fem to structure
        monopile["structure"] = monopile["internal_structure_2d_fem"]
        monopile.pop("internal_structure_2d_fem")
        # Now define common reference axis
        monopile["reference_axis"] = deepcopy(monopile["outer_shape"]["reference_axis"])
        # Pop out older ref_axis
        monopile["outer_shape"].pop("reference_axis")
        monopile["structure"].pop("reference_axis")
        # Rename drag_coefficient to cd
        cd_monopile = monopile["outer_shape"]["drag_coefficient"]
        monopile["outer_shape"]["cd"] = cd_monopile
        monopile["outer_shape"].pop("drag_coefficient")
        return dict_v2p0

    def convert_floating_platform(self, dict_v2p0):
        # Rad to deg in some inputs to floating platform

        members = dict_v2p0["components"]["floating_platform"]["members"]
        for i_memb in range(len(members)):
            # some renaming
            members[i_memb]["ca"] = members[i_memb]["Ca"]
            members[i_memb].pop("Ca")
            members[i_memb]["cd"] = members[i_memb]["Cd"]
            members[i_memb].pop("Cd")
            if "Cp" in members[i_memb]:
                members[i_memb]["cp"] = members[i_memb]["Cp"]
                members[i_memb].pop("Cp")
            members[i_memb]["structure"] = members[i_memb]["internal_structure"]
            members[i_memb].pop("internal_structure")
            if "ballasts" in members[i_memb]["structure"]:
                members[i_memb]["structure"]["ballast"] = members[i_memb]["structure"]["ballasts"]
                members[i_memb]["structure"].pop("ballasts")
            # switch from rad to deg
            if "angles" in members[i_memb]["outer_shape"]:
                angles_rad = members[i_memb]["outer_shape"]["angles"]
                members[i_memb]["outer_shape"]["angles"] = np.rad2deg(angles_rad)
            if "rotation" in members[i_memb]["outer_shape"]:
                rotation_rad = members[i_memb]["outer_shape"]["rotation"]
                members[i_memb]["outer_shape"]["rotation"] = np.rad2deg(rotation_rad)
        return dict_v2p0

    def convert_airfoils(self, dict_v2p0):
        # Airfoils: angle of attack in deg and cl, cd, cm tags
        for i_af in range(len(dict_v2p0["airfoils"])):
            af = dict_v2p0["airfoils"][i_af]
            af["rthick"] = af["relative_thickness"]
            af.pop("relative_thickness")
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
            
                plr["re_sets"] = [{}]
                plr["re_sets"][0]["re"] = plr["re"]
                plr.pop("re")
                plr["re_sets"][0]["cl"] = plr["cl"]
                plr.pop("cl")
                plr["re_sets"][0]["cd"] = plr["cd"]
                plr.pop("cd")
                plr["re_sets"][0]["cm"] = plr["cm"]
                plr.pop("cm")

                # To the first set, assign temporary tag default
                if i_plr==0:
                    af["polars"][i_plr]["configuration"] = "default"
                else:
                    af["polars"][i_plr]["configuration"] = "config%d"%i_plr
        return dict_v2p0
    
    def convert_materials(self, dict_v2p0):
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

        return dict_v2p0
    
    def convert_controls(self, dict_v2p0):

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

        return dict_v2p0


if __name__ == "__main__":
    
    from pathlib import Path

    turbine_reference_path = Path(windIO.turbine_ex.__file__).parent

    filename_v1p0 = r"../../test/turbine/v1p0/IEA-15-240-RWT.yaml" 
    filename_v2p0 = turbine_reference_path / "IEA-15-240-RWT_v2p0.yaml"
    
    if not os.path.exists(filename_v1p0):
        raise Exception("Point to an existing yaml file that you want to convert from windIO v1.0 to v2.0.")

    converter = v1p0_to_v2p0(filename_v1p0, filename_v2p0)
    converter.convert()
