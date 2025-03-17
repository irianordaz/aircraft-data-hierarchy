import sys
import openmdao.api as om
from aircraft_data_hierarchy.performanceLib.propulsion.propulsion_performance_builder import pyCycleBuilder
from utils.generate_demo_adh import generate_test_ADH_propulsion
from utils.ADH_JSON_tools import JSON_to_ADH, ADH_to_JSON
from aircraft_data_hierarchy.performanceLib.propulsion.utils.pycycle_to_ADH import initialize_engine_deck_ADH, append_data_point_ADH, append_data_point_json
from pydantic.v1 import utils
from aircraft_data_hierarchy.behaviorLib.propulsion.propulsion_cycle_behavior import (
    MultiPointCycle,
)

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


    prob.set_val("DESIGN.fc.alt", behavior.flight_conditions_design.alt[0], units="ft")
    prob.set_val("DESIGN.fc.MN", behavior.flight_conditions_design.mn[0])

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

if __name__ == "__main__":

    # Folder path for files
    output = "/home/mdolabuser/mount/aircraft-data-hierarchy/MichiganFinalPropulsionDemo/output_files/"

    # Load the generated test ADH
    ADHInstance= generate_test_ADH_propulsion()
    ADHInstance = JSON_to_ADH(output + "step1_adh.json", ADHInstance)

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

    # Promoted names for data that we want to write back to the ADH engine deck
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
    
    # Define the canonical order for the engine deck.
    ordered_keys = ["mn", "alt", "throttle", "gross_thrust", "net_thrust", "ram_drag", "fuel_flow", "temp", "shaft_power"]
    
    # Specify the JSON file path for the engine deck.
    json_file_path = output + "pycycle_engine.json"

    #Initialize the Engine Deck in the ADH (sets up the DaveML structure in the behavior branch but no data points yet)
    deck_index = initialize_engine_deck_ADH(prob, ADHInstance, promoted_names=promoted_names, ordered_keys=ordered_keys)


    # Start the main analysis loop over all Mach number altitude pairs
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

            #Write the data point to the ADHInstance
            append_data_point_ADH(prob, ADHInstance.behavior.engine_decks[deck_index].ungridded_table_def[0], promoted_names=promoted_names, ordered_keys=ordered_keys)

            #Write the data poin to JSON(for later use in Aviary)
            append_data_point_json(prob, json_file_path, promoted_names=promoted_names, ordered_keys=ordered_keys)


        # run throttle back up to full power
        for PC in [1, 0.85]:
            prob["OD_part_pwr.PC"] = PC
            prob.run_model()

    ADH_to_JSON(ADHInstance,output + "step2_adh.json")
        
