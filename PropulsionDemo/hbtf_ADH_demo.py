import numpy as np
from aircraft_data_hierarchy.performanceLib.propulsion.hbtf_builder import HBTFBuilder, MPhbtfBuilder
from aircraft_data_hierarchy.performanceLib.propulsion.propulsion_performance_builder import pyCycleBuilder
from generate_demo_adh import generate_test_ADH_propulsion
import openmdao.api as om

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

if __name__ == "__main__":
    ADHInstance = generate_test_ADH_propulsion()
    pycTest = pyCycleBuilder(ADHInstance)
    pycTest.getInput()

    prob = om.Problem()
    prob.model = pycTest.getOutput()

    prob.setup()

    # USER SCRIPT FOR RUNNING ANALYSIS BELOW THIS LINE
    # -----------------------------------------------
    prob, flight_env = HBTFprep(prob, ADHInstance)
    om.n2(prob, show_browser=False)
    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=1)

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
                # viewer(prob, "DESIGN", file=viewer_file)
                first_pass = False
            # viewer(prob, "OD_part_pwr", file=viewer_file)

        # run throttle back up to full power
        for PC in [1, 0.85]:
            prob["OD_part_pwr.PC"] = PC
            prob.run_model()

    outputs = prob.model.list_outputs(
        out_stream=None, residuals_tol=1e-2, implicit=True, explicit=False, residuals=True
    )

    from pprint import pprint

    with open("output.txt", "w") as f:
        pprint(outputs, stream=f)