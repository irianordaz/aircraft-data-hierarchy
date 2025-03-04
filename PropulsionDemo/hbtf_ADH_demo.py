from aircraft_data_hierarchy.performanceLib.propulsion.hbtf_builder import HBTFBuilder, MPhbtfBuilder
from aircraft_data_hierarchy.performanceLib.propulsion.propulsion_performance_builder import pyCycleBuilder
from generate_demo_adh import generate_test_ADH_propulsion
import openmdao.api as om
from pydantic.v1 import utils
from aircraft_data_hierarchy.behaviorLib.propulsion.propulsion_cycle_behavior import (
    MultiPointCycle,
)
import sys
import json
import os



# Temporarily disabled output to ADH funtionality until we can get access to the modified N3CC code next week

# utils_dir = os.path.abspath("/home/mdolabuser/mount/n3cc_demo_packages_npss_boeing_notwate/Aviary/aviary/subsystems/propulsion")
# if utils_dir not in sys.path:
#     sys.path.append(utils_dir)
# import engine_deck  
# from engine_deck import aliases

def HBTFprep(prob, ADHInstance):
    """
    Function that sets the initial guesses in the pyCycle problem and collects the flight condition pairs into a set of tuples
    """
    if utils.lenient_isinstance(ADHInstance.cycle, MultiPointCycle):
        cycle = ADHInstance.cycle.design_point
    else:
        cycle = ADHInstance.cycle
    behavior = ADHInstance.behavior
    # Set PR and eff

    prob.set_val("DESIGN.fan.PR", cycle.elements[1].pr_des)
    prob.set_val("DESIGN.fan.eff", cycle.elements[1].eff_des)

    prob.set_val("DESIGN.lpc.PR", cycle.elements[4].pr_des)
    prob.set_val("DESIGN.lpc.eff", cycle.elements[4].eff_des)

    prob.set_val("DESIGN.hpc.PR", cycle.elements[6].pr_des)
    prob.set_val("DESIGN.hpc.eff", cycle.elements[6].eff_des)

    prob.set_val("DESIGN.hpt.eff", cycle.elements[9].eff_des)
    prob.set_val("DESIGN.lpt.eff", cycle.elements[11].eff_des)

    # print(cycle.elements[1].pr_des)
    # print(cycle.elements[1].eff_des)
    # print(cycle.elements[4].pr_des)
    # print(cycle.elements[4].eff_des)
    # print(cycle.elements[6].pr_des)
    # print(cycle.elements[6].eff_des)
    # print(cycle.elements[9].eff_des)
    # print(cycle.elements[11].eff_des)

    prob.set_val("DESIGN.fc.alt", behavior.flight_conditions_design.alt[0], units="ft")
    prob.set_val("DESIGN.fc.MN", behavior.flight_conditions_design.mn[0])

    # print(behavior.flight_conditions_design.alt[0])
    # print(behavior.flight_conditions_design.mn[0])

    prob.set_val("DESIGN.T4_MAX", 2857, units="degR")
    prob.set_val("DESIGN.Fn_DES", 5900.0, units="lbf")  # TODO

    prob.set_val("OD_full_pwr.T4_MAX", 2857, units="degR")  # TODO
    prob.set_val("OD_part_pwr.PC", 0.8)

    # Set initial guesses for balances
    prob["DESIGN.balance.FAR"] = 0.025
    prob["DESIGN.balance.W"] = 100.0
    prob["DESIGN.balance.lpt_PR"] = 4.0
    prob["DESIGN.balance.hpt_PR"] = 3.0
    prob["DESIGN.fc.balance.Pt"] = 5.2
    prob["DESIGN.fc.balance.Tt"] = 440.0

    for pt in ADHInstance.cycle.od_points:

        print(pt.name)

        # initial guesses
        prob[pt.name + ".balance.FAR"] = 0.02467
        prob[pt.name + ".balance.W"] = 300
        prob[pt.name + ".balance.BPR"] = 5.105
        prob[pt.name + ".balance.lp_Nmech"] = 5000
        prob[pt.name + ".balance.hp_Nmech"] = 15000
        prob[pt.name + ".hpt.PR"] = 3.0
        prob[pt.name + ".lpt.PR"] = 4.0
        prob[pt.name + ".fan.map.RlineMap"] = 2.0
        prob[pt.name + ".lpc.map.RlineMap"] = 2.0
        prob[pt.name + ".hpc.map.RlineMap"] = 2.0

    ODpoints = ADHInstance.cycle.od_points
    machs = ODpoints[0].flight_conditions_od.mn
    alts = ODpoints[0].flight_conditions_od.alt

    flight_env = list(zip(machs, alts))

    print(flight_env)

    return prob, flight_env

def viewer(prob, pt, file=sys.stdout):
    """
    print a report of all the relevant cycle properties
    """

    if pt == 'DESIGN':
        MN = prob['DESIGN.fc.Fl_O:stat:MN']
        LPT_PR = prob['DESIGN.balance.lpt_PR']
        HPT_PR = prob['DESIGN.balance.hpt_PR']
        FAR = prob['DESIGN.balance.FAR']
    else:
        MN = prob[pt+'.fc.Fl_O:stat:MN']
        LPT_PR = prob[pt+'.lpt.PR']
        HPT_PR = prob[pt+'.hpt.PR']
        FAR = prob[pt+'.balance.FAR']

    summary_data = (MN, prob[pt+'.fc.alt'], prob[pt+'.inlet.Fl_O:stat:W'], prob[pt+'.perf.Fn'],
                        prob[pt+'.perf.Fg'], prob[pt+'.inlet.F_ram'], prob[pt+'.perf.OPR'],
                        prob[pt+'.perf.TSFC'], prob[pt+'.splitter.BPR'])
    
    # outputs = prob.model.list_outputs(
    #     out_stream=None, units=True
    # )

    # inputs = prob.model.list_inputs(
    #     out_stream=None, units=True
    # )

    # from pprint import pprint

    # with open("output.txt", "w") as f:
    #     pprint(outputs, stream=f)

    # with open("input.txt", "w") as f:
    #     pprint(inputs, stream=f)

    print(file=file, flush=True)
    print(file=file, flush=True)
    print(file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                              POINT:", pt, file=file, flush=True)
    print("----------------------------------------------------------------------------", file=file, flush=True)
    print("                       PERFORMANCE CHARACTERISTICS", file=file, flush=True)
    print("    Mach      Alt       W      Fn      Fg    Fram     OPR     TSFC      BPR ", file=file, flush=True)
    print(" %7.5f  %7.1f %7.3f %7.1f %7.1f %7.1f %7.3f  %7.5f  %7.3f" %summary_data, file=file, flush=True)

def normalize_string(s):
    """
    Normalize a string by stripping whitespace, replacing spaces with underscores,
    and converting to lowercase.
    """
    return s.strip().replace(" ", "_").lower()

def get_unit(prob, prom_key):
    """
    Searches the OpenMDAO model metadata for the variable corresponding to prom_key and
    returns its units. If not found, returns 'unitless'.
    """
    io_metadata = prob.model.get_io_metadata()
    norm_prom = normalize_string(prom_key)
    for meta_key, meta in io_metadata.items():
        if norm_prom in normalize_string(meta_key):
            return meta.get("units", "unitless")
    return "unitless"

def append_data_point(prob, json_filepath, promoted_names=None, ordered_keys=["mn", "alt", "throttle", "gross_thrust", "ram_drag", "fuel_flow", "nox_rate"]):
    """
    Retrieves key variables from an OpenMDAO problem instance using prob.get_val and appends
    a new data point to a JSON file in the ungridded_table_def format.

    The canonical order (and comment order) is:
         "mn, alt, throttle, gross_thrust, ram_drag, fuel_flow, nox_rate"

    Parameters:
      prob         : OpenMDAO problem instance.
      json_filepath: Path to the JSON file to which the data point will be appended.
      promoted_names (dict, optional): Mapping from canonical variable names to promoted names.
            Default values (adjust these as needed) are used if not provided.
    """

    independent_vars = []
    dependent_vars = []
    for alias in ordered_keys:
        if alias in ["mn", "alt", "throttle", "hybrid_throttle"]:
            independent_vars.append({
                "var_id": alias,
                "min": None,
                "max": None,
                "extrapolate": None,
                "interpolate": None
            })
        else:
            dependent_vars.append({"var_id": alias})

    if promoted_names is None:
        promoted_names = {
        "mn": "OD_part_pwr.fc.MN",
        "alt": "OD_part_pwr.fc.alt",
        "throttle": "OD_part_pwr.PC",
        "gross_thrust": "OD_part_pwr.perf.Fg",
        "net_thrust": "OD_part_pwr.perf.Fn",
        "ram_drag": "OD_part_pwr.perf.ram_drag",
        "fuel_flow": "OD_part_pwr.perf.Wfuel_0",
        "temp": "OD_full_pwr.T4_MAX",
        "shaft_power": "OD_part_pwr.lp_shaft.HPX"
        # PyCycle doesn't return nox rate 
    }

    # Retrieve values from OpenMDAO using prob.get_val.
    data_values = []
    for key in ordered_keys:
        prom_key = promoted_names.get(key)
        if prom_key is None:
            raise ValueError(f"Promoted name for '{key}' is not provided.")
        # Retrieve the value.
        val = prob.get_val(prom_key)
        try:
            val_float = float(val)
        except Exception as e:
            raise ValueError(f"Error converting value for '{key}' from promoted '{prom_key}' to float: {val}. Error: {e}")
        data_values.append(val_float)

    # Assemble the data point string.
    # Example: "0.0 0.0 21.0 1110.0 0.0 500.3 55.372 <!-- mn, alt, throttle, gross_thrust, ram_drag, fuel_flow, nox_rate-->"
    values_str = " ".join(str(v) for v in data_values)
    comment_str = " <!-- " + ", ".join(ordered_keys) + " -->"
    full_value_str = values_str + comment_str

    new_data_point = {
        "mod_id": None,
        "value": full_value_str
    }

    # If the JSON file exists, load it; otherwise, create a new JSON structure.
    if os.path.exists(json_filepath):
        with open(json_filepath, "r") as f:
            json_data = json.load(f)
    else:
        units_list = []
        for key in ordered_keys:
            prom_key = promoted_names.get(key)
            unit = get_unit(prob, prom_key)
            units_list.append(unit)
        units_string = ", ".join(units_list)

        json_data = {
            "file_header": None,
            "variable_def": None,
            "breakpoint_def": None,
            "gridded_table_def": None,
            "ungridded_table_def": {
                "name": None,
                "ut_id": None,
                "units": [units_string],
                "description": None,
                "provenance": None,
                "provenance_ref": None,
                "uncertainty": None,
                "data_point": []
            },
            "function": [
                {
                    "name": "Engine Deck",
                    "description": None,
                    "provenance": None,
                    "provenance_ref": None,
                    "independent_var_pts": None,
                    "dependent_var_pts": None,
                    "independent_var_ref": independent_vars,
                    "dependent_var_ref": dependent_vars,
                    "function_defn": None
                }
            ],
            "check_data": None
        }

    # Append the new data point.
    json_data["ungridded_table_def"]["data_point"].append(new_data_point)

    # Write the updated JSON back to file.
    with open(json_filepath, "w") as f:
        json.dump(json_data, f, indent=4)

    print(f"Appended new data point to {json_filepath}")

if __name__ == "__main__":
    # Generate a test propulsion ADH
    ADHInstance = generate_test_ADH_propulsion()

    # Intantiate the pyCycle builder class
    pycTest = pyCycleBuilder(ADHInstance)

    # Load inputs to builder from ADH
    pycTest.getInput()

    # Output the OpenMDAO model to the problem
    prob = om.Problem()
    prob.model = pycTest.getOutput()

    prob.setup()

    # USER SCRIPT FOR RUNNING ANALYSIS BELOW THIS LINE
    # -----------------------------------------------
    prob, flight_env = HBTFprep(prob, ADHInstance) #Sets initial guess and mach #, altitute pairs
    om.n2(prob, show_browser=False)
    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=1)

    # Promoted names for data that you want to write back to the ADH engine deck
    # promoted_names = {
    #     "mn": "OD_part_pwr.fc.MN",
    #     "alt": "OD_part_pwr.fc.alt",
    #     "throttle": "OD_part_pwr.PC",
    #     "gross_thrust": "OD_part_pwr.perf.Fg",
    #     "net_thrust": "OD_part_pwr.perf.Fn",
    #     "ram_drag": "OD_part_pwr.perf.ram_drag",
    #     "fuel_flow": "OD_part_pwr.perf.Wfuel_0",
    #     "temp": "OD_full_pwr.T4_MAX",
    #     "shaft_power": "OD_part_pwr.lp_shaft.HPX"
    #     # PyCycle doesn't return nox rate 
    # }
    
    # # Define the canonical order.
    # ordered_keys = ["mn", "alt", "throttle", "gross_thrust", "net_thrust", "ram_drag", "fuel_flow", "temp", "shaft_power"]
    
    # # Specify the JSON file path for the engine deck.
    # json_file_path = "pycycle_engine.json"

    viewer_file = open("hbtf_view.out", "w")
    first_pass = True
    for MN, alt in flight_env:

        # NOTE: You never change the MN,alt for the
        # design point because that is a fixed reference condition.

        print("***" * 10)
        print(f"* MN: {MN}, alt: {alt}")
        print("***" * 10)
        prob["OD_full_pwr.fc.MN"] = MN
        prob["OD_full_pwr.fc.alt"] = alt

        prob["OD_part_pwr.fc.MN"] = MN
        prob["OD_part_pwr.fc.alt"] = alt

        for PC in ADHInstance.cycle.od_points[1].PC:
            print(f"## PC = {PC}")
            prob["OD_part_pwr.PC"] = PC
            prob.run_model()

            if first_pass:
                viewer(prob, "DESIGN", file=viewer_file)
                first_pass = False
            viewer(prob, "OD_part_pwr", file=viewer_file)

        # run throttle back up to full power
        for PC in [1, 0.85]:
            prob["OD_part_pwr.PC"] = PC
            prob.run_model()
        
        # Temporarily disabled output deck to ADH until we can get access to the modified N3CC code next week
        #append_data_point(prob, json_file_path, promoted_names=promoted_names, ordered_keys=ordered_keys)
