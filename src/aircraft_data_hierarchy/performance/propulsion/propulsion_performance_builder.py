import numpy as np
from pydantic.v1 import utils
from aircraft_data_hierarchy.common_base_model import CommonBaseModel, Metadata
from aircraft_data_hierarchy.behavior import Behavior, DAVEfunc, FileHeader, Author
from aircraft_data_hierarchy.requirements import Requirement
from aircraft_data_hierarchy.performance import Discipline
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
    Performance,
)
from aircraft_data_hierarchy.performanceUtils.propulsion.hbtf_builder import HBTFBuilder
import openmdao.api as om


class PropulsionPerformanceBuilder:
    """A builder class intended to take an ADH instance from pydantic as input and then automatically run an analysis or optimization using the desired tool of choice.
    This parent class contains all the necessary input processing funciton from the ADH. The goal is for input from the ADH to be processed into python dictionaries as an
    intermediate step. This parent class contains the input function necessary to retreive ADH data from pydantic and return them as dictionaries so they can prepared for input into the desired tools.
    For example pyCycle has a python based interface while NPSS requires an input files. Using dictionaries as an intermediary between the tools and the ADH makes
    adapting a new tool for use with the AHD much easier.
    """

    """INIT: The Parent class takes an ADHInstance as input."""

    def __init__(self, ADHInstance):
        self.ADHInstance = ADHInstance

    """ ADH INPUT: A set of helper functions that retreive ADH data from pydantic and return them as dictionaries. """

    # Gets the general information about the cycle
    def getCycleInfo(self):
        cycle = self.ADHInstance.cycle
        cycleInfo = {
            "name": cycle.name,
            "design": cycle.design,
            "thermo_method": cycle.thermo_method,
            "thermo_data": cycle.thermo_data,
            "throttle_mode": cycle.throttle_mode,
            "global_connections": cycle.global_connections,
            "flow_connections": cycle.flow_connections,
            "solver_settings": cycle.solver_settings,
        }
        return cycleInfo

    # Gets the specified flight conditions for analysis
    def getFlightConds(self):
        engineElements = self.ADHInstance.cycle.elements
        flightconditions = []
        for element in engineElements:
            if utils.lenient_isinstance(element, FlightConditions):
                flightConds = {"name": element.name, "mn": element.mn, "alt": element.alt, "d_ts": element.d_ts}
                flightconditions.append(flightConds)
        return flightconditions

    # These functions get the engine elements

    def getInlet(self):
        engineElements = self.ADHInstance.cycle.elements
        inlets = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Inlet):
                inletData = {
                    "name": element.name,
                    "statics": element.statics,
                    "mn": element.mn,
                    "ram_recovery": element.ram_recovery,
                    "area": element.area,
                }
                inlets.append(inletData)
        return inlets

    def getSplitter(self):
        engineElements = self.ADHInstance.cycle.elements
        splitters = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Splitter):
                splitterData = {
                    "name": element.name,
                    "statics": element.statics,
                    "bpr": element.bpr,
                    "mn1": element.mn1,
                    "mn2": element.mn2,
                    "area1": element.area1,
                    "area2": element.area2,
                }
                splitters.append(splitterData)
        return splitters

    def getDuct(self):
        engineElements = self.ADHInstance.cycle.elements
        ducts = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Duct):
                ductData = {
                    "name": element.name,
                    "statics": element.statics,
                    "dPqP": element.dPqP,
                    "mn": element.mn,
                    "Q_dot": element.Q_dot,
                    "area": element.area,
                }
                ducts.append(ductData)
        return ducts

    def getCompressor(self):
        engineElements = self.ADHInstance.cycle.elements
        compressors = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Compressor):
                compData = {
                    "name": element.name,
                    "statics": element.statics,
                    "map_data": element.map_data,
                    "map_extrap": element.map_extrap,
                    "map_interp_method": element.map_interp_method,
                    "alpha_map": element.alpha_map,
                    "bleed_names": element.bleed_names,
                    "pr_des": element.pr_des,
                    "eff_des": element.eff_des,
                    "area": element.area,
                    "mn": element.mn,
                }
                compressors.append(compData)
        return compressors

    def getCombustor(self):
        engineElements = self.ADHInstance.cycle.elements
        combustors = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Combustor):
                combData = {
                    "name": element.name,
                    "statics": element.statics,
                    "dp_qp": element.dp_qp,
                    "FAR": element.FAR,
                    "area": element.area,
                    "mn": element.mn,
                    "fuel_type": element.fuel_type,
                }
                combustors.append(combData)
        return combustors

    def getTurbine(self):
        engineElements = self.ADHInstance.cycle.elements
        turbines = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Turbine):
                turbData = {
                    "name": element.name,
                    "statics": element.statics,
                    "map_data": element.map_data,
                    "map_extrap": element.map_extrap,
                    "map_interp_method": element.map_interp_method,
                    "alpha_map": element.alpha_map,
                    "pr_des": element.pr_des,
                    "eff_des": element.eff_des,
                    "bleed_names": element.bleed_names,
                    "area": element.area,
                    "mn": element.mn,
                }
                turbines.append(turbData)
        return turbines

    def getNozzle(self):
        engineElements = self.ADHInstance.cycle.elements
        nozzles = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Nozzle):
                nozzData = {
                    "name": element.name,
                    "statics": element.statics,
                    "nozz_type": element.nozz_type,
                    "loss_coef": element.loss_coef,
                    "cv": element.cv,
                    "area": element.area,
                    "mn": element.mn,
                }
                nozzles.append(nozzData)
        return nozzles

    def getShaft(self):
        engineElements = self.ADHInstance.cycle.elements
        shafts = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Shaft):
                shaftData = {
                    "name": element.name,
                    "num_ports": element.num_ports,
                    "nmech": element.nmech,
                    "nmech_type": element.nmech_type,
                }
                shafts.append(shaftData)
        return shafts

    def getBleed(self):
        engineElements = self.ADHInstance.cycle.elements
        bleeds = []
        for element in engineElements:
            if utils.lenient_isinstance(element, Bleed):
                bleedData = {
                    "name": element.name,
                    "statics": element.statics,
                    "bleed_names": element.bleed_names,
                }
                bleeds.append(bleedData)
        return bleeds

    # Get the balance component

    def getBalance(self):
        balanceComps = self.ADHInstance.cycle.balance_components
        balances = []
        for comp in balanceComps:
            if utils.lenient_isinstance(comp, BalanceComponent):
                balanceData = {
                    "name": comp.balance_name,
                    "units": comp.units,
                    "eq_units": comp.eq_units,
                    "lower": comp.lower,
                    "upper": comp.upper,
                    "lhs_name": comp.lhs_name,
                    "rhs_name": comp.rhs_name,
                    "rhs_val": comp.rhs_val,
                    "mult_val": comp.mult_val,
                    "use_mult": comp.use_mult,
                }
                balances.append(balanceData)
        return balances

    def getPerformance(self):
        perfComps = self.ADHInstance.cycle.performance_components
        performance = []
        for perf in perfComps:
            if utils.lenient_isinstance(perf, Performance):
                performanceData = {
                    "name": perf.name,
                    "pt2_source": perf.pt2_source,
                    "pt2": perf.pt2,
                    "pt3_source": perf.pt3_source,
                    "pt3": perf.pt3,
                    "wfuel_0_source": perf.wfuel_0_source,
                    "wfuel_0": perf.wfuel_0,
                    "ram_drag_source": perf.ram_drag_source,
                    "ram_drag": perf.ram_drag,
                    "fg_0_source": perf.fg_0_source,
                    "fg_0": perf.fg_0,
                    "fg_1_source": perf.fg_1_source,
                    "fg_1": perf.fg_1,
                    "fn": perf.fn,
                    "opr": perf.opr,
                    "tsfc": perf.tsfc,
                }
                performance.append(performanceData)
        return performance

    def getInput(self):
        """
        Primary function that prepares the input dictionaries.
        """

        self.cycleData = {
            "cycleInfo": self.getCycleInfo(),
            "fc": self.getFlightConds(),
            "inlets": self.getInlet(),
            "splitters": self.getSplitter(),
            "duct": self.getDuct(),
            "comp": self.getCompressor(),
            "comb": self.getCombustor(),
            "turb": self.getTurbine(),
            "nozz": self.getNozzle(),
            "shafts": self.getShaft(),
            "bleeds": self.getBleed(),
            "balances": self.getBalance(),
            "perf": self.getPerformance(),
        }

        return self.cycleData

    def transferData(self):
        """
        Reserved for any further intermediate processing required in child classes
        """
        pass

    def getOutput(self):
        """
        Reserved for ouput processing and tools execution in child classes
        """
        pass


class pyCycleBuilder(PropulsionPerformanceBuilder):
    """
    Child of the builder class. Input related functions in parent class. Any data processing required for pyCycle model construction and execute is
    specified here.
    """

    def getInput(self):
        """
        Handled by parent. Any other specified tasks for pyCycle can go here.
        """
        return super().getInput()

    def transferData(self):
        """
        Reserved
        """
        return super().transferData()

    def getOutput(self):
        """
        Returns the pyCycle builder class for HBTF for the engine type.
        Parameters
        """

        self.pycycleObject = HBTFBuilder(adhCycleData=self.cycleData)

        return self.pycycleObject


class NPSSBuilder(PropulsionPerformanceBuilder):
    def __init__(self, ADHInstance):
        raise Exception("NPSS Builder not implemented!")


if __name__ == "__main__":

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
    burner = Combustor(name="burner", fuel_type="FAR")
    hpt = Turbine(name="hpt", map_data="HPTMap", bleed_names=["cool3", "cool4"], map_extrap=True)
    duct11 = Duct(name="duct11")
    lpt = Turbine(name="lpt", bleed_names=["cool1", "cool2"], map_extrap=True)
    duct13 = Duct(name="duct13")
    core_nozz = Nozzle(name="core_nozz", nozz_type="CV", loss_coef="Cv")
    byp_bld = Bleed(name="byp_bld", bleed_names=["bypBld"])
    duct15 = Duct(name="duct15")
    byp_nozz = Nozzle(name="byp_nozz", nozz_type="CV", loss_coef="Cv")
    lp_shaft = Shaft(name="lp_shaft", num_ports=3)
    hp_shaft = Shaft(name="hp_shaft", num_ports=2)

    perf = Performance(
        name="perf",
        pt2_source="inlet",
        pt3_source="hpc",
        wfuel_0_source="burner",
        ram_drag_source="inlet",
        fg_0_source="core_nozz",
        fg_1_source="byp_nozz",
    )

    # Set PR and eff
    fan.pr_des = 1.685
    fan.eff_des = 0.8948

    lpc.pr_des = 1.935
    lpc.eff_des = 0.9243

    hpc.pr_des = 9.369
    hpc.eff_des = 0.8707

    cycle = PropulsionCycle(
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
        throttle_mode="T4",
        balance_components=[],
        performance_components=[perf],
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

    pycTest = pyCycleBuilder(ADHInstance)
    # print(pycTest.getInput())
    pycTest.getInput()

    prob = om.Problem()
    prob.model = pycTest.getOutput()

    prob.setup(check=True)
    om.n2(prob)
