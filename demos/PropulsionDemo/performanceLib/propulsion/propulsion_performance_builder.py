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
    Compressor,
    Turbine,
    Bleed,
    Nozzle,
    Shaft,
    Combustor,
)
from behaviorLib.propulsion.propulsion_cycle_behavior import (
    PropulsionCycleBehavior,
    Performance,
    FlightConditions,
    MultiPointCycle,
    OffDesignPoint,
)
from performanceLib.propulsion.propulsion_cycle_performance import (
    PropulsionCyclePerformance,
)
from performanceLib.propulsion.builders.hbtf_builder import HBTFBuilder, MPhbtfBuilder
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

    def getODPoints(self):
        cycle = self.ADHInstance.cycle
        od_points = []
        for od_pt in cycle.od_points:
            od_point = {
                "name": od_pt.name,
                "PC": od_pt.PC,
                "throttle_mode": od_pt.throttle_mode,
                "mn": od_pt.flight_conditions_od.mn,
                "alt": od_pt.flight_conditions_od.alt,
                "d_ts": od_pt.flight_conditions_od.d_ts,
            }
            od_points.append(od_point)
        return od_points

    # Gets the general information about the cycle
    def getCycleInfo(self):
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        cycleBeh = self.ADHInstance.behavior
        cyclePerf = self.ADHInstance.performance
        cycleInfo = {
            "name": cycle.name,
            "design": cycleBeh.design,
            "is_multi_point": False,
            "thermo_method": cyclePerf.thermo_method,
            "thermo_data": cyclePerf.thermo_data,
            "throttle_mode": cyclePerf.throttle_mode,
            "global_connections": cycle.global_connections,
            "flow_connections": cycle.flow_connections,
            "solver_settings": cyclePerf.solver_settings,
        }

        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycleInfo["is_multi_point"] = True
            cycleInfo["od_points"] = self.getODPoints()
        return cycleInfo

    # Gets the design flight conditions for analysis
    def getDesFlightConds(self):
        flightconditions = []
        des_fc = self.ADHInstance.behavior.flight_conditions_design
        flightConds = {"name": des_fc.name, "mn": des_fc.mn, "alt": des_fc.alt, "d_ts": des_fc.d_ts}
        flightconditions.append(flightConds)
        return flightconditions

    # These functions get the engine elements

    def getInlet(self):
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        inlets = []
        for element in engineElements:
            #if utils.lenient_isinstance(element, Inlet):
            if element.type == "inlet":
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
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        splitters = []
        for element in engineElements:
            if element.type == "splitter":
            #if utils.lenient_isinstance(element, Splitter):
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
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        ducts = []
        for element in engineElements:
            if element.type == "duct":
            #if utils.lenient_isinstance(element, Duct):
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
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        compressors = []
        for element in engineElements:
            if element.type == "comp":
            #if utils.lenient_isinstance(element, Compressor):
                compData = {
                    "name": element.name,
                    "statics": element.statics,
                    "map_data": element.map_data,
                    "map_extrap": element.map_extrap,
                    "map_interp_method": element.map_interp_method,
                    "bleed_names": element.bleed_names,
                    "pr_des": element.pr_des,
                    "eff_des": element.eff_des,
                    "area": element.area,
                    "mn": element.mn,
                    "frac_W": element.frac_W,
                    "frac_P": element.frac_P,
                    "frac_work": element.frac_work,
                }
                compressors.append(compData)
        return compressors

    def getCombustor(self):
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        combustors = []
        for element in engineElements:
            if element.type == "comb":
            #if utils.lenient_isinstance(element, Combustor):
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
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        turbines = []
        for element in engineElements:
            if element.type == "turb":
            #if utils.lenient_isinstance(element, Turbine):
                turbData = {
                    "name": element.name,
                    "statics": element.statics,
                    "map_data": element.map_data,
                    "map_extrap": element.map_extrap,
                    "map_interp_method": element.map_interp_method,
                    "pr_des": element.pr_des,
                    "eff_des": element.eff_des,
                    "bleed_names": element.bleed_names,
                    "area": element.area,
                    "mn": element.mn,
                    "frac_W": element.frac_W,
                    "frac_P": element.frac_P,
                    "frac_work": element.frac_work,
                }
                turbines.append(turbData)
        return turbines

    def getNozzle(self):
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        nozzles = []
        for element in engineElements:
            if element.type == "nozz":
            #if utils.lenient_isinstance(element, Nozzle):
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
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        shafts = []
        for element in engineElements:
            if element.type == "shaft":
            #if utils.lenient_isinstance(element, Shaft):
                shaftData = {
                    "name": element.name,
                    "num_ports": element.num_ports,
                    "nmech": element.nmech,
                    "nmech_type": element.nmech_type,
                    "HPX": element.HPX,
                }
                shafts.append(shaftData)
        return shafts

    def getBleed(self):
        if utils.lenient_isinstance(self.ADHInstance.cycle, MultiPointCycle):
            cycle = self.ADHInstance.cycle.design_point
        else:
            cycle = self.ADHInstance.cycle
        engineElements = cycle.elements
        bleeds = []
        for element in engineElements:
            if element.type == "bleed":
            #if utils.lenient_isinstance(element, Bleed):
                bleedData = {
                    "name": element.name,
                    "statics": element.statics,
                    "bleed_names": element.bleed_names,
                    "mn": element.mn,
                    "frac_W": element.frac_W,
                    "frac_P": element.frac_P,
                    "frac_work": element.frac_work,
                }
                bleeds.append(bleedData)
        return bleeds

    def getPerformance(self):
        perfComps = self.ADHInstance.behavior.performance_components
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
            "fc": self.getDesFlightConds(),
            "inlets": self.getInlet(),
            "splitters": self.getSplitter(),
            "duct": self.getDuct(),
            "comp": self.getCompressor(),
            "comb": self.getCombustor(),
            "turb": self.getTurbine(),
            "nozz": self.getNozzle(),
            "shafts": self.getShaft(),
            "bleeds": self.getBleed(),
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
        if self.cycleData["cycleInfo"]["is_multi_point"]:
            self.pycycleObject = MPhbtfBuilder(adhCycleData=self.cycleData)
        else:
            self.pycycleObject = HBTFBuilder(adhCycleData=self.cycleData)

        return self.pycycleObject


class NPSSBuilder(PropulsionPerformanceBuilder):
    def __init__(self, ADHInstance):
        raise Exception("NPSS Builder not implemented!")


