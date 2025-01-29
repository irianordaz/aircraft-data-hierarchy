from typing import List, Optional
from pydantic import Field, field_validator
from ...common_base_model import CommonBaseModel
from ...behavior import Behavior, UngriddedTableDef, DataPoint
from ...work_breakdown_structure.propulsion.propulsion_cycle import PropulsionCycle


class EngineElementBehavior(Behavior):
    """
    Represents an individual element in the engine cycle.

    Attributes:
        name (str): The name of the engine element.
        options (dict, optional): The options associated with the engine element.
    """

    name: str = Field(..., description="The name of the engine element.")
    options: Optional[dict] = Field(None, description="The options associated with the engine element.")


class Bleed(EngineElementBehavior):
    """
    Bleed output component

    Attributes
    ----------
    bleed_names : Optional[List[str]]
        Names of the bleed connections associated
    statics : Optional[bool]
        If true calculate static properties
    """

    area: Optional[dict] = Field(None, description="Off-design frontal areas.")
    statics: Optional[bool] = Field(None, description="If true calculate static properties")


class Inlet(EngineElementBehavior):
    """
    Inlet conditions for the engine.

    Attributes
    ----------
    area : Optional[dict]
        Off-design frontal area
    F_ram_off_design : Optional[dict]
        Calculated ram drag at off-design conditions.
    """

    area: Optional[dict] = Field(None, description="Off-design frontal area")
    F_ram_off_design: Optional[dict] = Field(None, description="Calculated ram drag at off-design conditions")


class Compressor(EngineElementBehavior):
    """
    Compressor component of the engine.

    Attributes
    ----------
    mn : Optional[float]
        Mach number.
    map_data : Optional[str]
        Map data for the compressor.
    bleed_names : Optional[List[str]]
        Names of the bleed ports.
    map_extrap : Optional[bool]
        Flag to indicate if map extrapolation is used.
    pr_des : Optional[float]
        Design condition pressure ratio
    eff_des : Optional[float]
        Design condition efficeincy
    """

    statics: Optional[bool] = Field(None, description="If true calculate static properties")
    s_pr: Optional[float] = Field(None, description="Design pressure ratio")
    s_eff: Optional[float] = Field(None, description="Design efficeincy")
    s_Wc: Optional[float] = Field(None, description="Design air mass flow rate")
    mn: Optional[dict] = Field(None, description="Off-design Mach number")
    area: Optional[dict] = Field(None, description="Off-design frontal area of component")
    PR: Optional[dict] = Field(None, description="Off-design pressure ratio")
    eff_poly: Optional[dict] = Field(None, description="Off-design efficeincy")
    Wc: Optional[dict] = Field(None, description="Off-design air mass flow rate")
    Nc: Optional[dict] = Field(None, description="Off-design Nc")
    pwr: Optional[dict] = Field(None, description="Off-design power")


class Splitter(EngineElementBehavior):
    """
    Splitter component of the engine.

    Attributes
    ----------
    bpr : Optional[float]
        Bypass ratio.
    mn1 : Optional[float]
        Mach number for the first flow path.
    mn2 : Optional[float]
        Mach number for the second flow path.
    area1 : Optional[float]
        Area for the second flow path.
    area2 : Optional[float]
        Area for the second flow path.
    """

    bpr: Optional[List[float]] = Field(None, description="Off-design Bypass ratio")
    mn1: Optional[List[float]] = Field(None, description="Off-design Mach number for the first flow path")
    mn2: Optional[List[float]] = Field(None, description="Off-design Mach number for the second flow path")
    area1: Optional[List[float]] = Field(None, description="Off-design Frontal area for the first flow path")
    area2: Optional[List[float]] = Field(None, description="Off-design Frontal area for the second flow path")


class Duct(EngineElementBehavior):
    """
    Duct component of the engine.

    Attributes
    ----------
    mn : Optional[float]
        Mach number.
    dp_qp : Optional[float]
        Design pressure loss.
    """

    s_dPqP: Optional[float] = Field(None, description="Design pressure loss")
    dPqP: Optional[dict] = Field(None, description="Off-design design pressure loss")
    Q_dot: Optional[dict] = Field(
        None, description="Off-design heat flow rate into (positive) or out of (negative) the air"
    )
    area: Optional[dict] = Field(None, description="Off-design frontal area of component")
    mn: Optional[dict] = Field(None, description="Off-design mach number")


class Combustor(EngineElementBehavior):
    """
    Combustor component of the engine.

    Attributes
    ----------
    fuel_type : Optional[str]
        Type of fuel used.
    mn : Optional[float]
        Mach number.
    dp_qp : Optional[float]
        Pressure drop ratio.
    """

    statics: Optional[bool] = Field(None, description="If true calculate static properties")
    mn: Optional[dict] = Field(None, description="Off-design mach number")
    dp_qp: Optional[dict] = Field(None, description="Off-design Pressure drop ratio")
    FAR: Optional[dict] = Field(None, description="Off-design fuel-air ratio")
    Wfuel: Optional[dict] = Field(None, description="Off-design fuel injection rate")
    area: Optional[dict] = Field(None, description="Off-design frontal area of component")


class Turbine(EngineElementBehavior):
    """
    Turbine component of the engine.

    Attributes
    ----------
    mn : Optional[float]
        Mach number.
    map_data : Optional[str]
        Map data for the turbine.
    bleed_names : Optional[List[str]]
        Names of the bleed ports.
    map_extrap : Optional[bool]
        Flag to indicate if map extrapolation is used.
    pr_des : Optional[float]
        Design condition pressure ratio
    effDes : Optional[float]
        Design condition efficeincy
    """

    statics: Optional[bool] = Field(None, description="If true calculate static properties")
    s_pr: Optional[float] = Field(None, description="Design pressure ratio")
    s_eff: Optional[float] = Field(None, description="Design efficeincy")
    s_Wc: Optional[float] = Field(None, description="Design air mass flow rate")
    mn: Optional[dict] = Field(None, description="Off-design Mach number")
    area: Optional[dict] = Field(None, description="Off-design frontal area of component")
    PR: Optional[dict] = Field(None, description="Off-design pressure ratio")
    eff_poly: Optional[dict] = Field(None, description="Off-design efficeincy")
    Wc: Optional[dict] = Field(None, description="Off-design air mass flow rate")
    Np: Optional[dict] = Field(None, description="Off-design Np")
    pwr: Optional[dict] = Field(None, description="Off-design power")
    trq: Optional[dict] = Field(None, description="Off-design torque")


class Nozzle(EngineElementBehavior):
    """
    Nozzle component of the engine.

    Attributes
    ----------
    nozz_type : Optional[str]
        Type of nozzle.
    loss_coef : Optional[str]
        Loss coefficient.
    cv : Optional[float]
        Discharge coefficient.
    """

    statics: Optional[bool] = Field(None, description="If true calculate static properties")
    mn: Optional[dict] = Field(None, description="Off-design mach number")
    area: Optional[dict] = Field(None, description="Off-design frontal area of component")


class Performance(Behavior):
    """
    Performance metrics of the engine.

    Attributes
    ----------
    pt2 : Optional[float]
        Total pressure at station 2.
    pt3 : Optional[float]
        Total pressure at station 3.
    wfuel_0 : Optional[float]
        Fuel flow rate.
    ram_drag : Optional[float]
        Ram drag.
    fg_0 : Optional[float]
        Gross thrust from core nozzle.
    fg_1 : Optional[float]
        Gross thrust from bypass nozzle.
    fn : Optional[float]
        Net thrust.
    opr : Optional[float]
        Overall pressure ratio.
    tsfc : Optional[float]
        Thrust specific fuel consumption.
    """

    name: Optional[str] = Field(None, description="Name of the performance component")
    pt2_source: Optional[str] = Field(None, description="Name of component to get Pt2 from")
    pt2: Optional[float] = Field(None, description="Total pressure at station 2")
    pt3_source: Optional[str] = Field(None, description="Name of component to get Pt3 from")
    pt3: Optional[float] = Field(None, description="Total pressure at station 3")
    wfuel_0_source: Optional[str] = Field(None, description="Name of component to get wfuel from")
    wfuel_0: Optional[float] = Field(None, description="Fuel flow rate")
    ram_drag_source: Optional[str] = Field(None, description="Name of component to get ram drag from")
    ram_drag: Optional[float] = Field(None, description="Ram drag")
    fg_0_source: Optional[str] = Field(None, description="Name of core nozzle component to get fg_0 from")
    fg_0: Optional[float] = Field(None, description="Gross thrust from core nozzle")
    fg_1_source: Optional[str] = Field(None, description="Name of bypass nozzle component to get fg_1 from")
    fg_1: Optional[float] = Field(None, description="Gross thrust from bypass nozzle")
    fn: Optional[float] = Field(None, description="Net thrust")
    opr: Optional[float] = Field(None, description="Overall pressure ratio")
    tsfc: Optional[float] = Field(None, description="Thrust specific fuel consumption")


class FlightConditions(CommonBaseModel):
    """
    Flight conditions for the engine.

    Attributes
    ----------
    mn : Optional[float]
        Mach number.
    alt : Optional[float]
        Altitude in feet.
    d_ts : Optional[float]
        Temperature deviation in degrees Rankine.
    W : Optional[float]
        Air mass flow rate.
    """

    name: str = Field(..., description="The name of the flight condition.")
    mn: Optional[List[float]] = Field(None, description="Mach number")
    alt: Optional[List[float]] = Field(None, description="Altitude in feet")
    d_ts: Optional[float] = Field(None, description="Temperature deviation in degrees Rankine")
    W: Optional[List[float]] = Field(None, description="Air mass flow rate")


class PropulsionCycleBehavior(Behavior):
    """
    Contains the analysis inputs and Engine Deck for a propulsion cycle analysis.

    Attributes:
        name (str): The name of the engine cycle.
        design (bool): Whether the engine cycle is in design mode.
        thermo_method (str, optional): The thermodynamic method used in the engine cycle. Defaults to 'CEA'.
        thermo_data (str, optional): The thermodynamic data used in the engine cycle.
        elements (List[EngineElement]): The list of engine elements in the engine cycle.
        balance_components (List[BalanceComponent], optional): The list of balance components in the engine cycle.
        global_connections (dict, optional): The global connections in the engine cycle.
        flow_connections (dict, optional): The flow connections in the engine cycle.
        solver_settings (dict, optional): The solver settings for the engine cycle.
    """

    name: str = Field(..., description="The name of the engine cycle analysis.")
    design: bool = Field(..., description="Whether the engine cycle is in design mode.")
    flight_conditions_design: Optional[FlightConditions] = Field(None, description="Design flight conditions.")
    performance_components: Optional[List[Performance]] = Field(
        None, description="The list of the performance components for the cycle."
    )


class OffDesignPoint(CommonBaseModel):
    """
    Represents an off-design point in a multi-point cycle analysis.

    Attributes:
        name (str): The name of the off-design point.
        parameters (dict): The parameter values for the off-design point.
    """

    name: str = Field(..., description="The name of the off-design point.")
    flight_conditions_od: Optional[FlightConditions] = Field(None, description="Off-design flight conditions.")
    PC: Optional[List[float]] = Field(None, description="List of off-design throttle percentage.")
    throttle_mode: str = Field("T4", description="What quanity should be used to throttle engine for off-design cases.")

    @field_validator("throttle_mode")
    def validate_throttle_mode(cls, v):
        allowed_methods = ["T4", "percent_thrust"]
        if v not in allowed_methods:
            raise ValueError(f"Throttle mode must be one of {allowed_methods}")
        return v


class MultiPointCycle(CommonBaseModel):
    """
    Represents a multi-point cycle analysis.

    Attributes:
        design_point (PropulsionCycle): The design point engine cycle.
        od_points (List[OffDesignPoint]): The list of off-design points.
        global_des_od_connections (dict, optional): The global design-to-off-design connections.
        design_constants (dict, optional): The design constants for the multi-point cycle analysis.
        seq_points (List[str], optional): The sequence of points in the multi-point cycle analysis.
    """

    design_point: PropulsionCycle = Field(..., description="The design point engine cycle.")
    od_points: List[OffDesignPoint] = Field(..., description="The list of off-design points.")
    global_des_od_connections: Optional[dict] = Field(None, description="The global design-to-off-design connections.")
    design_constants: Optional[dict] = Field(
        None, description="The design constants for the multi-point cycle analysis."
    )
    seq_points: Optional[List[str]] = Field(
        None, description="The sequence of points in the multi-point cycle analysis."
    )


class EngineDeckData(DataPoint):
    """
    Contains ADH engine deck values.

    Attributes
    ----------
        mn : Optional[float]
            Mach number.
        alt: Optional[float]
            Altitude.
        throttle: Optional[float]
            Throttle.
        gross_thrust: Optional[float]
            Gross Thrust.
        ram_drag: Optional[float]
            Ram Drag.
        fuel_flow: Optional[float]
            Fuel Flow.
        nox_rate: Optional[float]
            NOx Rate.

    """

    mn: Optional[float] = Field(None, description="Mach Number (unitless)")
    alt: Optional[float] = Field(None, description="Altitude (ft)")
    throttle: Optional[float] = Field(None, description="Throttle (unitless)")
    gross_thrust: Optional[float] = Field(None, description="Gross Thrust (lbf)")
    ram_drag: Optional[float] = Field(None, description="Ram Drag (lbf)")
    fuel_flow: Optional[float] = Field(None, description="Fuel Flow (lb/h)")
    nox_rate: Optional[float] = Field(None, description="NOx Rate (lb/h)")


class EngineDeckCompiled(UngriddedTableDef):
    """
    Assigns ADH Deck values into ungridded table format.

    Attributes
    ----------

    """

    flight_cond: Optional[List[EngineDeckData]] = Field(
        None, description="The list of the engine deck values for a flight condition."
    )
