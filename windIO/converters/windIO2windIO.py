#!/usr/bin/env python
import argparse
import sys
import os
import traceback
from copy import deepcopy
import numpy as np
import windIO


class v1p0_to_v2p1:
    def __init__(self, filename_v1p0, filename_v2px, **kwargs) -> None:
        self.filename_v1p0 = filename_v1p0
        self.filename_v2px = filename_v2px

        os.makedirs(os.path.dirname(os.path.realpath(self.filename_v2px)), exist_ok=True)

    def convert(self):
        print("Converter windIO v1.0 to v2.1 started.")

        print("Load file %s:"%self.filename_v1p0)

        # Read the input yaml
        dict_v1p0 = windIO.load_yaml(self.filename_v1p0)
        
        # Set windIO version
        self.dict_v2px = dict_v2px = {"windIO_version": "2.1"}

        # Copy the input windio dict
        dict_v2px.update(deepcopy(dict_v1p0))

        if "description" in dict_v2px:
            dict_v2px["comments"] = dict_v2px["description"]
            dict_v2px.pop("description")

        try:
            dict_v2px = self.convert_blade(dict_v2px)
            print("Blade converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Blade component could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        try:
            dict_v2px = self.convert_nacelle(dict_v2px)
            print("Nacelle converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Nacelle component could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        try:
            dict_v2px = self.convert_tower(dict_v2px)
            print("Tower converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Tower component could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        if "monopile" in dict_v2px["components"]:
            try:
                dict_v2px = self.convert_monopile(dict_v2px)
                print("Monopile converted successfully")
            except Exception as e:
                print(traceback.format_exc())
                print("⚠️ Monopile component could not be converted successfully. Please check.")
                print(f"Error details: {e}")
        if "floating_platform" in dict_v2px["components"]:
            try:
                dict_v2px = self.convert_floating_platform(dict_v2px)
                print("Floating platform converted successfully")
            except Exception as e:
                print(traceback.format_exc())
                print("⚠️ Floating platform component could not be converted successfully. Please check.")
                print(f"Error details: {e}")
        try:
            dict_v2px = self.convert_airfoils(dict_v2px)
            print("Airfoil database converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Airfoil database could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        try:
            dict_v2px = self.convert_materials(dict_v2px)
            print("Material database converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Material database could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        try:
            dict_v2px = self.convert_controls(dict_v2px)
            print("Control block converted successfully")
        except Exception as e:
            print(traceback.format_exc())
            print("⚠️ Control block database could not be converted successfully. Please check.")
            print(f"Error details: {e}")
        
        # If present, remove WISDEM specific environment, bos, and costs properties from schema
        if "environment" in dict_v2px:
            dict_v2px.pop("environment")
        if "bos" in dict_v2px:
            dict_v2px.pop("bos")
        if "costs" in dict_v2px:
            dict_v2px.pop("costs")

        # Print out
        print("New yaml file being generated: %s"%self.filename_v2px)
        windIO.yaml.write_yaml(dict_v2px, self.filename_v2px)
        
        print("Converter windIO v1.0 to v2.1 ended.")

    def convert_blade(self, dict_v2px):
        dict_v2px = self.convert_blade_reference_axis(dict_v2px)
        dict_v2px = self.convert_blade_outer_shape(dict_v2px)
        dict_v2px = self.convert_blade_structure(dict_v2px)
        if "elastic_properties_mb" in dict_v2px["components"]["blade"]:
            if "six_x_six" in dict_v2px["components"]["blade"]["elastic_properties_mb"]:
                dict_v2px = self.convert_elastic_properties(dict_v2px)
        return dict_v2px
    
    def convert_blade_reference_axis(self, dict_v2px):
        
        # New common ref axis for all blade subfields, take the aero shape one by default
        dict_v2px["components"]["blade"]["reference_axis"] = deepcopy(dict_v2px["components"]["blade"]["outer_shape_bem"]["reference_axis"])
        dict_v2px["components"]["blade"]["outer_shape_bem"].pop("reference_axis")

        return dict_v2px
    
    def convert_blade_outer_shape(self, dict_v2px):
        # Start by changing name
        dict_v2px["components"]["blade"]["outer_shape"] = dict_v2px["components"]["blade"]["outer_shape_bem"]
        dict_v2px["components"]["blade"].pop("outer_shape_bem")
        
        # Switch from pitch_axis to section_offset_y
        # First interpolate on chord grid
        blade_os = dict_v2px["components"]["blade"]["outer_shape"]
        pitch_axis_grid =  blade_os["pitch_axis"]["grid"]
        pitch_axis_values =  blade_os["pitch_axis"]["values"]
        chord_grid =  blade_os["chord"]["grid"]
        chord_values =  blade_os["chord"]["values"]
        section_offset_y_grid = chord_grid
        pitch_axis_interp = np.interp(section_offset_y_grid,
                                      pitch_axis_grid,
                                      pitch_axis_values,
                                      )
        # Now dimensionalize offset using chord
        section_offset_y_values = pitch_axis_interp * chord_values
        blade_os.pop("pitch_axis")
        blade_os["section_offset_y"] = {}
        blade_os["section_offset_y"]["grid"] = section_offset_y_grid
        blade_os["section_offset_y"]["values"] = section_offset_y_values
        
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
            n_af_available = len(dict_v2px["airfoils"])
            for i in range(n_af):
                for j in range(n_af_available):
                    if blade_os["airfoil_position"]["labels"][i] == dict_v2px["airfoils"][j]["name"]:
                        rthick_v1p0[i] = dict_v2px["airfoils"][j]["relative_thickness"]
            from scipy.interpolate import PchipInterpolator
            spline = PchipInterpolator
            rthick_spline = spline(blade_os["airfoil_position"]["grid"], rthick_v1p0)
            rthick = rthick_spline(chord_grid)
            rthick[rthick>1.]=1.
            blade_os["rthick"] = {}
            blade_os["rthick"]["grid"] = chord_grid
            blade_os["rthick"]["values"] = rthick

        blade_os.pop("airfoil_position")

        return dict_v2px
    
    def convert_blade_structure(self, dict_v2px):
        # Start by changing name
        dict_v2px["components"]["blade"]["structure"] = dict_v2px["components"]["blade"]["internal_structure_2d_fem"]
        dict_v2px["components"]["blade"].pop("internal_structure_2d_fem")
        # Convert field `rotation` from rad to deg when defined in webs/layers
        # Also, switch label offset_y_pa to offset_y_reference_axis
        blade_struct = dict_v2px["components"]["blade"]["structure"]
        layers_v1p0 = deepcopy(dict_v2px["components"]["blade"]["structure"]["layers"])
        webs_v1p0 = deepcopy(dict_v2px["components"]["blade"]["structure"]["webs"])

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
                start_nd_grid = layer_v1p0["start_nd_arc"]["grid"][0]
                end_nd_grid = layer_v1p0["start_nd_arc"]["grid"][-1]
            else:
                start_nd_grid = layer_v1p0["thickness"]["grid"][0]
                end_nd_grid = layer_v1p0["thickness"]["grid"][-1]

            zeros_dict = {"grid": [start_nd_grid, end_nd_grid],
                          "values": [0.0, 0.0]}
            ones_dict = {"grid": [start_nd_grid, end_nd_grid],
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
                if "fixed" in layer_v1p0["midpoint_nd_arc"]:
                    anchor["midpoint_nd_arc"] = {}
                    anchor["midpoint_nd_arc"]["anchor"] = {"name": layer_v1p0["midpoint_nd_arc"]["fixed"],
                                                           "handle": "start_nd_arc"}
                    if layer_v1p0["midpoint_nd_arc"]["fixed"] == "LE":
                        print("⚠️ Computing LE anchor from layer %s, please check!" % layer_v1p0["name"])
                        LE = (np.array(layer_v1p0["end_nd_arc"]["values"]) + np.array(layer_v1p0["start_nd_arc"]["values"])) / 2.0
                        LE_anchor = {"name": "LE",
                                     "start_nd_arc": {"grid": layer_v1p0["start_nd_arc"]["grid"],
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

        return dict_v2px

    def convert_elastic_properties(self, dict_v2px):
        # Start by changing name
        dict_v2px["components"]["blade"]["elastic_properties"] = dict_v2px["components"]["blade"]["elastic_properties_mb"]
        dict_v2px["components"]["blade"].pop("elastic_properties_mb")
        # Redefine stiffness and inertia matrices listing each element individually as opposed to an array
        dict_v2px["components"]["blade"]["structure"]["elastic_properties"] = dict_v2px["components"]["blade"]["elastic_properties"]["six_x_six"]
        blade_beam = dict_v2px["components"]["blade"]["structure"]["elastic_properties"]
        dict_v2px["components"]["blade"].pop("elastic_properties")

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

        
        return dict_v2px

    def convert_nacelle(self, dict_v2px):
        
        # Cone angle from rad to deg
        cone_rad = dict_v2px["components"]["hub"]["cone_angle"]
        dict_v2px["components"]["hub"]["cone_angle"] = np.rad2deg(cone_rad)

        # Hub drag coefficient to cd
        dict_v2px["components"]["hub"]["cd"] = dict_v2px["components"]["hub"]["drag_coefficient"]
        dict_v2px["components"]["hub"].pop("drag_coefficient")

        # Hub rigid-body mass properties. v1 stores these on
        # hub.elastic_properties_mb (system_mass / system_inertia /
        # system_center_mass, hub-aligned frame with x along the shaft); v2 uses
        # a `rigid_body` (mass, inertia[6], location[3]) in the same frame.
        if "elastic_properties_mb" in dict_v2px["components"]["hub"]:
            hub_epm = dict_v2px["components"]["hub"].pop("elastic_properties_mb")
            hub_ep = {}
            if "system_mass" in hub_epm:
                hub_ep["mass"] = hub_epm["system_mass"]
            inertia = hub_epm.get("system_inertia")
            if inertia is not None:
                inertia = list(inertia)
                if len(inertia) < 6:
                    inertia = inertia + [0.0] * (6 - len(inertia))
                hub_ep["inertia"] = inertia
            if "system_center_mass" in hub_epm:
                hub_ep["location"] = hub_epm["system_center_mass"]
            if hub_ep:
                dict_v2px["components"]["hub"]["elastic_properties"] = hub_ep

        # Split nacelle components
        v1p1_dt = deepcopy(dict_v2px["components"]["nacelle"]["drivetrain"])
        v1p1_nac = deepcopy(dict_v2px["components"]["nacelle"])
        dict_v2px["components"]["drivetrain"] = {}
        dict_v2px["components"]["drivetrain"]["outer_shape"] = {}
        if "uptilt" in v1p1_dt:
            uptilt_rad = v1p1_dt["uptilt"]
            dict_v2px["components"]["drivetrain"]["outer_shape"]["uptilt"] = np.rad2deg(uptilt_rad)
        if "distance_tt_hub" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["outer_shape"]["distance_tt_hub"] = v1p1_dt["distance_tt_hub"]
        if "distance_hub2mb" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["outer_shape"]["distance_hub_mb"] = v1p1_dt["distance_hub2mb"]
        if "distance_mb2mb" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["outer_shape"]["distance_mb_mb"] = v1p1_dt["distance_mb2mb"]
        if "overhang" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["outer_shape"]["overhang"] = v1p1_dt["overhang"]
        if "drag_coefficient" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["outer_shape"]["cd"] = v1p1_dt["drag_coefficient"]

        dict_v2px["components"]["drivetrain"]["gearbox"] = {}
        if "gear_ratio" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["gearbox"]["gear_ratio"] =  v1p1_dt["gear_ratio"]
        if "length_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["gearbox"]["length"] = v1p1_dt["length_user"]
        if "radius_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["gearbox"]["radius"] = v1p1_dt["radius_user"]
        if "mass_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["gearbox"]["mass"] = v1p1_dt["mass_user"]
        if "gearbox_efficiency" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["gearbox"]["efficiency"] = v1p1_dt["gearbox_efficiency"]
        if "damping_ratio" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["gearbox"]["damping_ratio"] = v1p1_dt["damping_ratio"]
        if "gear_configuration" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["gearbox"]["gear_configuration"] = v1p1_dt["gear_configuration"]
        if "planet_numbers" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["gearbox"]["planet_numbers"] = v1p1_dt["planet_numbers"]
        
        dict_v2px["components"]["drivetrain"]["lss"] = {}
        if "lss_length" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["lss"]["length"] = v1p1_dt["lss_length"]
        if "lss_diameter" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["lss"]["diameter"] = v1p1_dt["lss_diameter"]
        if "lss_wall_thickness" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["lss"]["wall_thickness"] = v1p1_dt["lss_wall_thickness"]
        if "lss_material" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["lss"]["material"] = v1p1_dt["lss_material"]

        dict_v2px["components"]["drivetrain"]["hss"] = {}
        if "hss_length" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["hss"]["length"] = v1p1_dt["hss_length"]
        if "hss_diameter" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["hss"]["diameter"] = v1p1_dt["hss_diameter"]
        if "hss_wall_thickness" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["hss"]["wall_thickness"] = v1p1_dt["hss_wall_thickness"]
        if "hss_material" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["hss"]["material"] = v1p1_dt["hss_material"]

        dict_v2px["components"]["drivetrain"]["nose"] = {}
        if "nose_diameter" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["nose"]["diameter"] = v1p1_dt["nose_diameter"]
        if "nose_wall_thickness" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["nose"]["wall_thickness"] = v1p1_dt["nose_wall_thickness"]
        
        dict_v2px["components"]["drivetrain"]["bedplate"] = {}
        if "bedplate_wall_thickness" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["bedplate"]["wall_thickness"] = v1p1_dt["bedplate_wall_thickness"]
        if "bedplate_flange_width" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["bedplate"]["flange_width"] = v1p1_dt["bedplate_flange_width"]
        if "bedplate_flange_thickness" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["bedplate"]["flange_thickness"] = v1p1_dt["bedplate_flange_thickness"]
        if "bedplate_web_thickness" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["bedplate"]["web_thickness"] = v1p1_dt["bedplate_web_thickness"]
        if "bedplate_material" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["bedplate"]["material"] = v1p1_dt["bedplate_material"]

        dict_v2px["components"]["drivetrain"]["other_components"] = {}
        if "brake_mass_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["other_components"]["brake_mass"] = v1p1_dt["brake_mass_user"]
        if "hvac_mass_coefficient" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["other_components"]["hvac_mass_coefficient"] = v1p1_dt["hvac_mass_coefficient"]
        if "converter_mass_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["other_components"]["converter_mass"] = v1p1_dt["converter_mass_user"]
        if "transformer_mass_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["other_components"]["transformer_mass"] = v1p1_dt["transformer_mass_user"]
        if "mb1Type" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["other_components"]["mb1Type"] = v1p1_dt["mb1Type"]
        if "mb2Type" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["other_components"]["mb2Type"] = v1p1_dt["mb2Type"]
        if "uptower" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["other_components"]["uptower"] = v1p1_dt["uptower"]

        dict_v2px["components"]["drivetrain"]["generator"] = {}
        if "generator" in v1p1_nac:
            #dict_v2px["components"]["drivetrain"]["generator"] = deepcopy(v1p1_nac["generator"])
            if "generator_length" in v1p1_nac["generator"]:
                dict_v2px["components"]["drivetrain"]["generator"]["length"] = v1p1_nac["generator"]["generator_length"]
                if "generator_length" in dict_v2px["components"]["drivetrain"]["generator"]:
                    dict_v2px["components"]["drivetrain"]["generator"].pop("generator_length")
            else:
                if "generator_length" in v1p1_dt:
                    dict_v2px["components"]["drivetrain"]["generator"]["length"] = v1p1_dt["generator_length"]
        if "generator_radius_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["generator"]["radius"] = v1p1_dt["generator_radius_user"]
        if "generator_mass_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["generator"]["mass"] = v1p1_dt["generator_mass_user"]
        if "rpm_efficiency_user" in v1p1_dt:
            dict_v2px["components"]["drivetrain"]["generator"]["rpm_efficiency"] = v1p1_dt["rpm_efficiency_user"]

        # Rigid-body mass properties. In v1 these live on
        # nacelle.drivetrain.elastic_properties_mb (system_mass / system_inertia
        # [/ system_inertia_tt] / system_center_mass + yaw_mass). v2 splits them
        # into a `rigid_body` (mass, inertia[6], location[3]) on the drivetrain
        # (tower-top coordinate system) and a separate `yaw` component.
        if "elastic_properties_mb" in v1p1_dt:
            epm = v1p1_dt["elastic_properties_mb"]
            dt_ep = {}
            if "system_mass" in epm:
                dt_ep["mass"] = epm["system_mass"]
            # Prefer the tower-top-frame inertia (matches the v2 drivetrain
            # frame); fall back to system_inertia. Pad the diagonal-only (len 3)
            # form to the full 6-element [Ixx, Iyy, Izz, Ixy, Ixz, Iyz] array.
            inertia = epm.get("system_inertia_tt", epm.get("system_inertia"))
            if inertia is not None:
                inertia = list(inertia)
                if len(inertia) < 6:
                    inertia = inertia + [0.0] * (6 - len(inertia))
                dt_ep["inertia"] = inertia
            if "system_center_mass" in epm:
                dt_ep["location"] = epm["system_center_mass"]
            if dt_ep:
                dict_v2px["components"]["drivetrain"]["elastic_properties"] = dt_ep
            if "yaw_mass" in epm:
                dict_v2px["components"]["yaw"] = {
                    "elastic_properties": {"mass": epm["yaw_mass"]}
                }

        dict_v2px["components"].pop("nacelle")


        return dict_v2px

    def convert_tower(self, dict_v2px):
        tower = dict_v2px["components"]["tower"]
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
        return dict_v2px

    def convert_monopile(self, dict_v2px):
        monopile = dict_v2px["components"]["monopile"]
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
        return dict_v2px

    def convert_floating_platform(self, dict_v2px):
        # Rad to deg in some inputs to floating platform
        joints = dict_v2px["components"]["floating_platform"]["joints"]
        for i_joint in range(len(joints)):
            if "cylindrical" in joints[i_joint] and joints[i_joint]["cylindrical"]:
                joints[i_joint]["location"][1] = np.rad2deg( joints[i_joint]["location"][1] )
        
        members = dict_v2px["components"]["floating_platform"]["members"]
        for i_memb in range(len(members)):
            # some renaming
            #members[i_memb]["ca"] = members[i_memb]["Ca"]
            #members[i_memb].pop("Ca")
            #members[i_memb]["cd"] = members[i_memb]["Cd"]
            #members[i_memb].pop("Cd")
            #if "Cp" in members[i_memb]:
            #    members[i_memb]["cp"] = members[i_memb]["Cp"]
            #    members[i_memb].pop("Cp")
            members[i_memb]["structure"] = members[i_memb]["internal_structure"]
            members[i_memb].pop("internal_structure")
            if "ballasts" in members[i_memb]["structure"]:
                members[i_memb]["structure"]["ballast"] = members[i_memb]["structure"]["ballasts"]
                members[i_memb]["structure"].pop("ballasts")
            # switch from rad to deg
            if "angles" in members[i_memb]["outer_shape"]:
                angles_rad = members[i_memb]["outer_shape"]["angles"]
                if angles_rad < 0.5*np.pi:
                    members[i_memb]["outer_shape"]["angles"] = np.rad2deg(angles_rad)
            if "rotation" in members[i_memb]["outer_shape"]:
                rotation_rad = members[i_memb]["outer_shape"]["rotation"]
                if rotation_rad < 0.5*np.pi:
                    members[i_memb]["outer_shape"]["rotation"] = np.rad2deg(rotation_rad)
            if "longitudinal_stiffeners" in members[i_memb]["structure"]:
                spacing_rad = members[i_memb]["structure"]["longitudinal_stiffeners"]["spacing"]
                if spacing_rad < 0.5*np.pi:
                    members[i_memb]["structure"]["longitudinal_stiffeners"]["spacing"] = np.rad2deg(spacing_rad)
        return dict_v2px

    def convert_airfoils(self, dict_v2px):
        # Airfoils: angle of attack in deg and cl, cd, cm tags
        for i_af in range(len(dict_v2px["airfoils"])):
            af = dict_v2px["airfoils"][i_af]
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
        return dict_v2px
    
    def convert_materials(self, dict_v2px):
        # Materials
        # manufacturing_id instead of component_id
        for i_mat in range(len(dict_v2px["materials"])):
            if "component_id" in dict_v2px["materials"][i_mat]:
                dict_v2px["materials"][i_mat]["manufacturing_id"] = dict_v2px["materials"][i_mat]["component_id"]
                dict_v2px["materials"][i_mat].pop("component_id")
            if "alp0" in dict_v2px["materials"][i_mat]:
                alp0_rad = dict_v2px["materials"][i_mat]["alp0"]
                if alp0_rad < np.pi:
                    dict_v2px["materials"][i_mat]["alp0"] = np.rad2deg(alp0_rad)

        return dict_v2px
    
    def convert_controls(self, dict_v2px):
        # Map the v1 nested control (supervisory/pitch/torque/yaw) onto the flat
        # 2.x control block, converting rad -> deg and rad/s -> rpm. Only the
        # turbine-level fields available in v1 are emitted; controller-tuning
        # fields (ROSCO-style gains, filter/actuator settings, gain-schedule
        # tables) are not present in v1 and are therefore omitted.
        v1_control = dict_v2px["control"]
        pitch = v1_control.get("pitch", {})
        torque = v1_control.get("torque", {})
        supervisory = v1_control.get("supervisory", {})
        yaw = v1_control.get("yaw", {})

        flat = {}
        if "rated_power" in dict_v2px.get("assembly", {}):
            flat["rated_power"] = dict_v2px["assembly"]["rated_power"]
        if "VS_minspd" in torque:  # rad/s -> rpm
            flat["min_rotor_speed"] = torque["VS_minspd"] * 30.0 / np.pi
        if "VS_maxspd" in torque:  # rated rotor speed, rad/s -> rpm
            flat["rated_rotor_speed"] = torque["VS_maxspd"] * 30.0 / np.pi
        if "tsr" in torque:
            flat["optimal_tsr"] = torque["tsr"]
        if "max_torque_rate" in torque:
            flat["max_torque_rate"] = torque["max_torque_rate"]
        if "min_pitch" in pitch:  # rad -> deg
            flat["min_pitch_limit"] = np.rad2deg(pitch["min_pitch"])
            flat["fine_pitch"] = np.rad2deg(pitch["min_pitch"])
        if "max_pitch" in pitch:  # rad -> deg
            flat["max_pitch_limit"] = np.rad2deg(pitch["max_pitch"])
        if "max_pitch_rate" in pitch:  # rad/s -> deg/s
            flat["max_pitch_rate"] = np.rad2deg(pitch["max_pitch_rate"])
        if "ps_percent" in pitch:
            flat["peak_thrust_shaving"] = pitch["ps_percent"]
        if "maxTS" in supervisory:
            flat["max_allowable_blade_tip_speed"] = supervisory["maxTS"]
        if "yaw_rate" in yaw:
            flat["yaw_rate"] = yaw["yaw_rate"]

        dict_v2px["control"] = flat
        return dict_v2px
    
class v2p0_to_v2p1:

    def __init__(self, filename_v2p0, filename_v2px):
        self.filename_v2p0 = filename_v2p0
        self.filename_v2px = filename_v2px

        os.makedirs(os.path.dirname(os.path.realpath(self.filename_v2px)), exist_ok=True)

    def convert(self):
        # Load v2.0 file
        dict_v2p0 = windIO.load_yaml(self.filename_v2p0)

        # Start with a copy of v2.0
        dict_v2px = deepcopy(dict_v2p0)

        # Currently, only controls are updated in v2.1
        dict_v2px = self.convert_controls(dict_v2px)

        # Save v2.1 file
        windIO.yaml.write_yaml(dict_v2px, self.filename_v2px)
        print(f"Converted windIO v2.0 file {self.filename_v2p0} to windIO v2.1 file {self.filename_v2px}.")
        return dict_v2px
    
    def convert_controls(self, dict_v2px):
        # Controls, update a few fields from rad to deg and from rad/s to rpm
        
        # Switch these fields over to new names
        dict_v2px["control"]["min_pitch_limit"] = dict_v2px["control"]["pitch"]["min_pitch"]
        dict_v2px["control"]["max_pitch_limit"] = dict_v2px["control"]["pitch"]["max_pitch"]
        dict_v2px["control"]["max_pitch_rate"]  = dict_v2px["control"]["pitch"]["max_pitch_rate"]
        dict_v2px["control"]["min_rotor_speed"] = dict_v2px["control"]["torque"]["VS_minspd"]
        dict_v2px["control"]["max_rotor_speed"] = dict_v2px["control"]["torque"]["VS_maxspd"]

        # Remove these sub-fields
        if "supervisory" in dict_v2px["control"]:
            dict_v2px["control"].pop("supervisory")
        if "torque" in dict_v2px["control"]:
            dict_v2px["control"].pop("torque")
        if "pitch" in dict_v2px["control"]:
            dict_v2px["control"].pop("pitch")
        if "shutdown" in dict_v2px["control"]:
            dict_v2px["control"].pop("shutdown")
        return dict_v2px

    
def run():
    parser = argparse.ArgumentParser(description="WindIO v1->v2 Converter")
    parser.add_argument("-i", "--input", help="Input v1 filename path")
    parser.add_argument("-o", "--output", help="Output v2 filename path")
    args = parser.parse_args()

    filename_v1p0 = args.input
    filename_v2p0 = args.output
    
    if not os.path.exists(filename_v1p0):
        raise Exception(f"Cannot find input windIO v1.0 file: {filename_v1p0}.")

    converter = v1p0_to_v2p0(filename_v1p0, filename_v2p0)
    converter.convert()

    # Convert from v2.0 to v2.1
    converter_2 = v2p0_to_v2px(filename_v2p0, filename_v2p0)
    converter_2.convert()
        
    sys.exit(0)

    
if __name__ == "__main__":
    run()
    
