import numpy as np
from high_bypass_turbofan import HBTF, viewer, MPhbtf, daveml_viewer
import openmdao.api as om
from aircraft_data_hierarchy.common_base_model import CommonBaseModel, Metadata
from aircraft_data_hierarchy.requirements import Requirement
from aircraft_data_hierarchy.performance import Discipline
from aircraft_data_hierarchy.behavior import DAVEfunc, FileHeader, Author
from aircraft_data_hierarchy.work_breakdown_structure.propulsion import (
    Propulsion,
    PropulsionCycle,
    FlightConditions,
    Inlet,
    Compressor,
    Splitter,
    Duct,
    Compressor,
    Turbine,
    Bleed,
    Nozzle,
    Shaft,
    Combustor,
    BalanceComponent,
)


def setupADHHBPPropulsion():
    #Set-up the ADH Propulsion instance for demo purposes

    metadata = Metadata(key="example_key", value="example_value")

    fc = FlightConditions(name="fc", mn=[0.8], alt=[35000])
    inlet = Inlet(name="inlet")
    fan = Compressor(name="fan")
    splitter = Splitter(name="splitter")
    duct4 = Duct(name="duct4")
    lpc = Compressor(name="lpc")
    duct6 = Duct(name="duct6")
    hpc = Compressor(name="hpc", bleed_names=["cool1", "cool2", "cust"])
    bld3 = Bleed(name="bld3", bleed_names=["cool3", "cool4"])
    burner = Combustor(name="burner")
    hpt = Turbine(name="hpt", bleed_names=["cool3", "cool4"])
    duct11 = Duct(name="duct11")
    lpt = Turbine(name="lpt", bleed_names=["cool1", "cool2"])
    duct13 = Duct(name="duct13")
    core_nozz = Nozzle(name="core_nozzle", nozz_type="CV", loss_coef="Cv")
    byp_bld = Bleed(name="byp_bld", bleed_names=["bypBld"])
    duct15 = Duct(name="duct15")
    byp_nozz = Nozzle(name="byp_nozz", nozz_type="CV", loss_coef="Cv")
    lp_shaft = Shaft(name="lp_shaft", num_ports=3)
    hp_shaft = Shaft(name="hp_shaft", num_ports=2)

    #Set PR and eff
    fan.pr_des = 1.685
    fan.eff_des = 0.8948

    lpc.pr_des = 1.935
    lpc.eff_des = 0.9243

    hpc.pr_des = 9.369
    hpc.eff_des = 0.8707
    
    ADHInstance = PropulsionCycle(
        name="Cycle",
        design=True,
        elements=[
            fc,
            inlet,
            fan,
            splitter,
            duct4,
            lpc,
            duct6,
            hpc,
            bld3,
            burner,
            hpt,
            duct11,
            lpt,
            duct13,
            core_nozz,
            byp_bld,
            duct15,
            byp_nozz,
            lp_shaft,
            hp_shaft,
        ],
        thermo_method="TABULAR",
        balance_components=[],
    )

    file_header = FileHeader(name="engineDeck", author=[Author(name="Safa Bakhshi")])

    ADHInstance = Propulsion(
        name="Engine",
        description="Main engine component",
        requirements=[
            Requirement(
                name="Req1",
                description="Requirement 1",
                priority="High",
                verification_method="Test",
                status="Open",
                acceptance_criteria="Criteria 1",
            )
        ],
        subcomponents=[],
        metadata=metadata,
        cycle=cycle,
        performance=[Discipline(name="Performance1", description="Performance description")],
        temp_behavior=DAVEfunc(file_header=file_header),
    )

    return ADHInstance


def runpyCycle(ADHInstance):
    import time

    prob = om.Problem()
    prob.model = mp_hbtf = MPhbtf()  #pyCycle HBTF
    prob.setup()

    prob.set_val("DESIGN.fan.PR", ADHInstance.cycle.elements[2].pr_des)
    prob.set_val("DESIGN.fan.eff", ADHInstance.cycle.elements[2].eff_des)


    prob.set_val("DESIGN.lpc.PR", ADHInstance.cycle.elements[5].pr_des)
    prob.set_val("DESIGN.lpc.eff", ADHInstance.cycle.elements[5].eff_des)


    prob.set_val("DESIGN.hpc.PR", ADHInstance.cycle.elements[7].pr_des)
    prob.set_val("DESIGN.hpc.eff", ADHInstance.cycle.elements[7].eff_des)


    prob.set_val("DESIGN.hpt.PR", ADHInstance.cycle.elements[10].eff_des)
    prob.set_val("DESIGN.lpt.eff", ADHInstance.cycle.elements[12].eff_des)

    prob.set_val("DESIGN.fc.alt", ADHInstance.cycle.elements[0].alt)
    prob.set_val("DESIGN.fc.MN", ADHInstance.cycle.elements[0].mn)

    prob.set_val("DESIGN.T4_MAX", 2857, units="degR")
    prob.set_val("DESIGN.Fn_DES", 5900.0, units="lbf")

    prob.set_val("OD_full_pwr.T4_MAX", 2857, units="degR")
    prob.set_val("OD_part_pwr.PC", 0.8)

    # Set initial guesses for balances
    prob["DESIGN.balance.FAR"] = 0.025
    prob["DESIGN.balance.W"] = 100.0
    prob["DESIGN.balance.lpt_PR"] = 4.0
    prob["DESIGN.balance.hpt_PR"] = 3.0
    prob["DESIGN.fc.balance.Pt"] = 5.2
    prob["DESIGN.fc.balance.Tt"] = 440.0

    for pt in ["OD_full_pwr", "OD_part_pwr"]:

        # initial guesses
        prob[pt + ".balance.FAR"] = 0.02467
        prob[pt + ".balance.W"] = 300
        prob[pt + ".balance.BPR"] = 5.105
        prob[pt + ".balance.lp_Nmech"] = 5000
        prob[pt + ".balance.hp_Nmech"] = 15000
        prob[pt + ".hpt.PR"] = 3.0
        prob[pt + ".lpt.PR"] = 4.0
        prob[pt + ".fan.map.RlineMap"] = 2.0
        prob[pt + ".lpc.map.RlineMap"] = 2.0
        prob[pt + ".hpc.map.RlineMap"] = 2.0

    st = time.time()

    prob.set_solver_print(level=-1)
    prob.set_solver_print(level=2, depth=1)

    flight_env = [(0.8, 35000), (0.4, 35000),
                  (0.4, 20000), (0.8, 20000), 
                  (0.8, 10000), (0.4, 10000),
                  (.001, 1000), (0.2, 1000)]

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

        for PC in [1, 0.9, 0.8, .7]:
            print(f"## PC = {PC}")
            prob["OD_part_pwr.PC"] = PC
            prob.run_model()

            if first_pass:
                prop = daveml_viewer(prob, "DESIGN", ADHInstance, first_pass, file=viewer_file)
                first_pass = False
            daveml_viewer(prob, "OD_part_pwr", ADHInstance, first_pass, file=viewer_file)

        # run throttle back up to full power
        #for PC in [1, 0.85]:
            #prob["OD_part_pwr.PC"] = PC
            #prob.run_model()

    print()
    print("Run time", time.time() - st)
    return ADHInstance




if __name__ == "__main__":
    propulsion = setupADHHBPPropulsion()
    propulsion = runpyCycle(propulsion)
    print(propulsion.temp_behavior.gridded_table_def)

# hello