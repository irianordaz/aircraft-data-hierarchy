import numpy as np
from pydantic.v1 import utils
from aircraft_data_hierarchy.common_base_model import CommonBaseModel, Metadata
from aircraft_data_hierarchy.behavior import Behavior, DAVEfunc, FileHeader, Author
from aircraft_data_hierarchy.work_breakdown_structure.propulsion import (
    Propulsion,
    PropulsionCycle,
    Inlet,
    Compressor,
    Splitter,
    Duct,
    Turbine,
    Bleed,
    Nozzle,
    Shaft,
    Combustor,
)
from aircraft_data_hierarchy.behaviorLib.propulsion.propulsion_cycle_behavior import (
    PropulsionCycleBehavior,
    Performance,
    FlightConditions,
    MultiPointCycle,
    OffDesignPoint,
)
from aircraft_data_hierarchy.performanceLib.propulsion.propulsion_cycle_performance import (
    PropulsionCyclePerformance,
)
from aircraft_data_hierarchy.performanceLib.propulsion.builders.hbtf_builder import HBTFBuilder, MPhbtfBuilder

def generate_test_ADH_propulsion():
    # Set-up the ADH Propulsion instance for demo purposes

    metadata = Metadata(key="example_key", value="example_value")

    fc = FlightConditions(name="fc", mn=[0.8], alt=[35000])
    inlet = Inlet(name="inlet")
    fan = Compressor(name="fan", map_data="FanMap", bleed_names=[], map_extrap=True)
    splitter = Splitter(name="splitter")
    duct4 = Duct(name="duct4")
    lpc = Compressor(name="lpc", map_data="LPCMap", bleed_names=[], map_extrap=True)
    duct6 = Duct(name="duct6")
    hpc = Compressor(name="hpc", map_data="HPCMap", bleed_names=["cool1", "cool2", "cust"], map_extrap=True)
    bld3 = Bleed(name="bld3", bleed_names=["cool3", "cool4"])
    burner = Combustor(name="burner", fuel_type="Jet-A(g)")
    hpt = Turbine(name="hpt", map_data="HPTMap", bleed_names=["cool3", "cool4"], map_extrap=True)
    duct11 = Duct(name="duct11")
    lpt = Turbine(name="lpt", map_data="LPTMap", bleed_names=["cool1", "cool2"], map_extrap=True)
    duct13 = Duct(name="duct13")
    core_nozz = Nozzle(name="core_nozz", nozz_type="CV", loss_coef="Cv")
    byp_bld = Bleed(name="byp_bld", bleed_names=["bypBld"])
    duct15 = Duct(name="duct15")
    byp_nozz = Nozzle(name="byp_nozz", nozz_type="CV", loss_coef="Cv")
    lp_shaft = Shaft(name="lp_shaft", nmech_type="LP", num_ports=3)
    hp_shaft = Shaft(name="hp_shaft", nmech_type="HP", num_ports=2)

    perf = Performance(
        name="perf",
        pt2_source="inlet",
        pt3_source="hpc",
        wfuel_0_source="burner",
        ram_drag_source="inlet",
        fg_0_source="core_nozz",
        fg_1_source="byp_nozz",
    )

    # Set data

    # Inlet
    inlet.mn = 0.751
    inlet.ram_recovery = 0.999

    # Fan
    fan.mn = 0.4578

    # Comps
    lpc.mn = 0.3059
    hpc.mn = 0.2442
    hpc.frac_W = [0.050708, 0.020274, 0.0445]
    hpc.frac_P = [0.5, 0.55, 0.5]
    hpc.frac_work = [0.5, 0.5, 0.5]

    # Splitter
    splitter.bpr = 5.105
    splitter.mn1 = 0.3104
    splitter.mn2 = 0.4518

    # Ducts
    duct4.mn = 0.3121
    duct6.mn = 0.3563
    duct11.mn = 0.3063
    duct13.mn = 0.4463
    duct15.mn = 0.4589

    duct4.dPqP = 0.0048
    duct6.dPqP = 0.0101
    duct11.dPqP = 0.0051
    duct13.dPqP = 0.0107
    duct15.dPqP = 0.0149

    # Bleeds
    bld3.mn = 0.300
    byp_bld.mn = 0.4489

    bld3.frac_W = [0.067214, 0.101256]
    byp_bld.frac_W = [0.005]

    # Combs
    burner.mn = 0.1025
    burner.dp_qp = 0.0540

    # Turbs

    lpt.mn = 0.4127
    hpt.mn = 0.3650

    hpt.frac_P = [1.0, 0.0]
    lpt.frac_P = [1.0, 0.0]

    # Nozzle

    core_nozz.cv = 0.9933
    byp_nozz.cv = 0.9939

    # Set PR and eff
    fan.pr_des = 1.685
    fan.eff_des = 0.8948

    lpc.pr_des = 1.935
    lpc.eff_des = 0.9243

    hpc.pr_des = 9.369
    hpc.eff_des = 0.8707

    hpt.eff_des = 0.8888
    lpt.eff_des = 0.8996

    cycle = PropulsionCycle(
        name="Cycle",
        elements=[
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
        global_connections=["fan,lp_shaft", "lpc,lp_shaft", "lpt,lp_shaft", "hpc,hp_shaft", "hpt,hp_shaft"],
        flow_connections=[
            ["fc", "inlet"],
            ["inlet", "fan"],
            ["fan", "splitter"],
            ["splitter", "duct4", "1"],
            ["duct4", "lpc"],
            ["lpc", "duct6"],
            ["duct6", "hpc"],
            ["hpc", "bld3"],
            ["bld3", "burner"],
            ["burner", "hpt"],
            ["hpt", "duct11"],
            ["duct11", "lpt"],
            ["lpt", "duct13"],
            ["duct13", "core_nozz"],
            ["splitter", "byp_bld", "2"],
            ["byp_bld", "duct15"],
            ["duct15", "byp_nozz"],
        ],
    )

    cyclePerformance = PropulsionCyclePerformance(
        name="CyclePerformance",
        thermo_method="CEA",
        throttle_mode="T4",
    )

    cycleBehavior = PropulsionCycleBehavior(
        name="CycleBehavior",
        design=True,
        flight_conditions_design=fc,
        performance_components=[perf],
    )

    file_header = FileHeader(name="engineDeck", author=[Author(name="Safa Bakhshi")])

    ODpoints = []
    fc2 = FlightConditions(
        name="od_full_pwr_fc",
        mn=[0.8, 0.7, 0.4, 0.6, 0.8, 0.6, 0.4, 0.2, 0.001, 0.001, 0.2, 0.4, 0.6, 0.6, 0.4, 0.2, 0.001],
        alt=[35000, 35000, 20000, 20000, 20000, 10000, 10000, 10000, 10000, 1000, 1000, 1000, 1000, 0, 0, 0, 0],
        d_ts=0.0,
    )
    fc3 = FlightConditions(
        name="od_part_pwr_fc",
        mn=[0.8, 0.7, 0.4, 0.8, 0.6, 0.4, 0.6, 0.4, 0.2],
        alt=[35000, 35000, 35000, 10000, 10000, 10000, 0, 0, 0],
        d_ts=0.0,
    )

    od1 = OffDesignPoint(
        name="OD_full_pwr",
        flight_conditions_od=fc2,
        throttle_mode="T4",
    )

    od2 = OffDesignPoint(
        name="OD_part_pwr",
        flight_conditions_od=fc3,
        PC=[1.0, 0.8],
        throttle_mode="percent_thrust",
    )

    multipoint = MultiPointCycle(
        design_point=cycle,
        od_points=[od1, od2],
    )

    ADHInstance = Propulsion(
        name="Engine",
        description="Main engine component",
        subcomponents=[],
        metadata=metadata,
        cycle=multipoint,
        performance=cyclePerformance,
        behavior=cycleBehavior,
    )

    return ADHInstance