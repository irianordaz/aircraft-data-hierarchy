import numpy as np

import openmdao.api as om
import pycycle.api as pyc


class HBTFBuilder(pyc.Cycle):
    """
    Builder class that creates a single-point pyCycle HBTF model using data from the ADH instance as input.
    This builder class is based on the pyCycle HBTF example. It sets critical cycle parameters then searches
    the ADH data for each component of the engine and then adds the appropriate pyCycle class to the OpenMDAO
    model with associated settings. In then connects the components in the OpenMDAO model using the ADH data.

    TODO:
    - The Balance component connections are still hard coded in this script. Implementing them in the ADH will require some thought
    - The Solver settings are still hard coded in the script
    - Initial guesses and other necessary information for the solver to run still needs to be implemented in the ADH
    """

    """COMPONENTS: Class methods used by the builder class to add pyCycle components to the OpenMDAO model"""

    # Add engine elements to model

    def add_compressors(self, compressors):
        for comp in compressors:
            if comp["map_data"] == "FanMap":
                md = pyc.FanMap
                prom_nmech = "LP_Nmech"
            elif comp["map_data"] == "LPCMap":
                md = pyc.LPCMap
                prom_nmech = "LP_Nmech"
            elif comp["map_data"] == "HPCMap":
                md = pyc.HPCMap
                prom_nmech = "HP_Nmech"
            else:
                md = pyc.HPCMap
                prom_nmech = "HP_Nmech"  # TODO: Filter out case in ADH
            self.add_subsystem(
                comp["name"],
                pyc.Compressor(map_data=md, bleed_names=comp["bleed_names"], map_extrap=comp["map_extrap"]),
                promotes_inputs=[("Nmech", prom_nmech)],
            )

    def add_turbines(self, turbines):
        for turb in turbines:
            if turb["map_data"] == "LPTMap":
                md = pyc.LPTMap
                prom_nmech = "LP_Nmech"
            elif turb["map_data"] == "HPTMap":
                md = pyc.HPTMap
                prom_nmech = "HP_Nmech"
            else:
                md = pyc.HPTMap
                prom_nmech = "HP_Nmech"  # TODO: Filter out case in ADH
            self.add_subsystem(
                turb["name"],
                pyc.Turbine(map_data=md, bleed_names=turb["bleed_names"], map_extrap=turb["map_extrap"]),
                promotes_inputs=[("Nmech", prom_nmech)],
            )

    def add_combustors(self, combustors):
        for comb in combustors:
            self.add_subsystem(comb["name"], pyc.Combustor(fuel_type=comb["fuel_type"]))

    def add_shafts(self, shafts):
        for shaft in shafts:
            self.add_subsystem(
                shaft["name"],
                pyc.Shaft(num_ports=shaft["num_ports"]),
                promotes_inputs=[("Nmech", "{}_Nmech".format(shaft["nmech_type"]))],
            )

    def add_bleeds(self, bleeds):
        for bleed in bleeds:
            self.add_subsystem(bleed["name"], pyc.BleedOut(bleed_names=bleed["bleed_names"]))

    def add_flightconditions(self, flightconditions):
        for fc in flightconditions:
            self.add_subsystem(fc["name"], pyc.FlightConditions())

    def add_inlets(self, inlets):
        for inlet in inlets:
            self.add_subsystem(inlet["name"], pyc.Inlet())

    def add_splitters(self, splitters):
        for splitter in splitters:
            self.add_subsystem(splitter["name"], pyc.Splitter())

    def add_ducts(self, ducts):
        for duct in ducts:
            self.add_subsystem(duct["name"], pyc.Duct())

    def add_nozzles(self, nozzles):
        for nozz in nozzles:
            self.add_subsystem(nozz["name"], pyc.Nozzle(nozzType=nozz["nozz_type"], lossCoef=nozz["loss_coef"]))

    # Add balance components to model

    def add_balances(self, balanceComp, balances, design):
        for bal in balances:
            if bal.on_design == design:
                balanceComp.add_balance(
                    bal.balance_name,
                    units=bal.units,
                    eq_units=bal.eq_units,
                    lower=bal.lower,
                    upper=bal.upper,
                    val=bal.val,
                    use_mult=bal.mult_val,
                )

    # Add Performance Component
    def add_perfomance(self, cycleData):
        for perf in cycleData["perf"]:
            self.add_subsystem(
                perf["name"],
                pyc.Performance(num_nozzles=len(cycleData["nozz"]), num_burners=len(cycleData["comb"])),
            )

            self.connect("{}.Fl_O:tot:P".format(perf["pt2_source"]), "{}.Pt2".format(perf["name"]))
            self.connect("{}.F_ram".format(perf["ram_drag_source"]), "{}.ram_drag".format(perf["name"]))

            self.connect("{}.Fl_O:tot:P".format(perf["pt3_source"]), "{}.Pt3".format(perf["name"]))

            self.connect("{}.Wfuel".format(perf["wfuel_0_source"]), "{}.Wfuel_0".format(perf["name"]))

            self.connect("{}.Fg".format(perf["fg_0_source"]), "{}.Fg_0".format(perf["name"]))

            self.connect("{}.Fg".format(perf["fg_1_source"]), "{}.Fg_1".format(perf["name"]))

    """CONNECTIONS: Class methods used by the builder class to connect pyCycle components in the OpenMDAO model"""

    # Connect the flow between engine elements
    def connect_flow(self, flow_connections):
        for fc in flow_connections:
            if len(fc) > 2:
                self.pyc_connect_flow("{}.Fl_O{}".format(fc[0], fc[2]), "{}.Fl_I".format(fc[1]))
            else:
                self.pyc_connect_flow("{}.Fl_O".format(fc[0]), "{}.Fl_I".format(fc[1]))

    # Connect the bleeds flows automatically based on the names specified by the user in the ADH
    def connect_bleeds(self, cycleData):
        # Convert pydantic to a dictionary with the component and bleed information
        bleedNames = set(
            [name for comp in cycleData["comp"] for name in comp["bleed_names"]]
            + [name for turb in cycleData["turb"] for name in turb["bleed_names"]]
            + [name for bleed in cycleData["bleeds"] for name in bleed["bleed_names"]]
        )

        bleedPairs = {}

        for comp in cycleData["comp"]:
            bleedPairs[comp["name"]] = comp["bleed_names"]
        for bleed in cycleData["bleeds"]:
            bleedPairs[bleed["name"]] = bleed["bleed_names"]
        for turb in cycleData["turb"]:
            bleedPairs[turb["name"]] = turb["bleed_names"]

        # Go through each bleed, find its components, then connect it in the model
        for bn in bleedNames:
            cWB = [key for key, values in bleedPairs.items() if bn in values]
            if len(cWB) > 1:
                self.pyc_connect_flow("{}.{}".format(cWB[0], bn), "{}.{}".format(cWB[1], bn), connect_stat=False)

    # Connects turbomachinery components to the shafts as specified by the user
    def connect_compturb_to_shafts(self, compturb, shafts, gc):
        for shaft in shafts:
            # print(shaft["name"])
            i = 0
            for comp in compturb:
                # print(comp["name"])
                # print(i)
                if "{},{}".format(comp["name"], shaft["name"]) in gc:
                    # print("{},{} Found in GC".format(comp["name"],shaft["name"]))
                    # print('{}.trq to {}.trq_{} CONNECTED'.format(comp["name"],shaft["name"],str(i)))
                    self.connect("{}.trq".format(comp["name"]), "{}.trq_{}".format(shaft["name"], str(i)))
                    i += 1

    # Connects the nozzle exit conditions to flight condition to get a perfectly expanded nozzle flow
    def connect_nozz_to_fc(self, nozzles, flightconditions):
        for fc in flightconditions:
            for i, nozz in enumerate(nozzles):
                self.connect("{}.Fl_O:stat:P".format(fc["name"]), "{}.Ps_exhaust".format(nozz["name"]))

    """OPENMDAO: Main OpenMDAO setup functions"""

    def initialize(self):
        """Declare the cycle data from ADH as input"""
        self.options.declare("adhCycleData")
        self.options.declare("throttle_mode", default="T4", values=["T4", "percent_thrust"])
        super().initialize()

    def setup(self):
        # Initialize the model here by setting option variables such as a switch for design vs off-des cases. Setup data from ADH
        self.cycleData = cycleData = self.options["adhCycleData"]

        self.options["throttle_mode"] = cycleData["cycleInfo"]["throttle_mode"]
        design = cycleData["cycleInfo"]["design"]

        if cycleData["cycleInfo"]["thermo_method"] == "TABULAR":
            self.options["thermo_method"] = "TABULAR"
            self.options["thermo_data"] = pyc.AIR_JETA_TAB_SPEC
        else:
            self.options["thermo_method"] = "CEA"
            self.options["thermo_data"] = pyc.species_data.janaf

        # Add all the engine components from the ADH using helper functions

        self.add_flightconditions(cycleData["fc"])
        self.add_inlets(cycleData["inlets"])
        self.add_compressors(cycleData["comp"])
        self.add_splitters(cycleData["splitters"])
        self.add_ducts(cycleData["duct"])
        self.add_bleeds(cycleData["bleeds"])
        self.add_combustors(cycleData["comb"])
        self.add_turbines(cycleData["turb"])
        self.add_nozzles(cycleData["nozz"])
        self.add_shafts(cycleData["shafts"])

        # Add and connect the performance component
        self.add_perfomance(cycleData)

        # Connect turbo machinery to shafts
        self.connect_compturb_to_shafts(
            cycleData["comp"], cycleData["shafts"], cycleData["cycleInfo"]["global_connections"]
        )

        # Ideally expanding flow by conneting flight condition static pressure to nozzle exhaust pressure
        self.connect_nozz_to_fc(cycleData["nozz"], cycleData["fc"])

        ##Add the balance component using the helper function.
        # Balances can be a bit confusing, here's some explanation -
        #   State Variables:
        #           (W)        Inlet mass flow rate to implictly balance thrust
        #                      LHS: perf.Fn  == RHS: Thrust requirement (set when TF is instantiated)
        #
        #           (FAR)      Fuel-air ratio to balance Tt4
        #                      LHS: burner.Fl_O:tot:T  == RHS: Tt4 target (set when TF is instantiated)
        #
        #           (lpt_PR)   LPT press ratio to balance shaft power on the low spool
        #           (hpt_PR)   HPT press ratio to balance shaft power on the high spool
        # Ref: look at the XDSM diagrams in the pyCycle paper and this:
        # http://openmdao.org/twodocs/versions/latest/features/building_blocks/components/balance_comp.html
        # if cycleData["balances"] is not None:
        balance = self.add_subsystem("balance", om.BalanceComp())
        # self.add_balances(balance ,cycleData["balances"] ,design)

        # TODO: The balance connections are hardcoded here until I can figure out how to implement their specification in the ADH
        if design:
            balance.add_balance("W", units="lbm/s", eq_units="lbf")
            # Here balance.W is implicit state variable that is the OUTPUT of balance object
            self.connect("balance.W", "fc.W")  # Connect the output of balance to the relevant input
            self.connect("perf.Fn", "balance.lhs:W")  # This statement makes perf.Fn the LHS of the balance eqn.
            self.promotes("balance", inputs=[("rhs:W", "Fn_DES")])

            balance.add_balance("FAR", eq_units="degR", lower=1e-4, val=0.017)
            self.connect("balance.FAR", "burner.Fl_I:FAR")
            self.connect("burner.Fl_O:tot:T", "balance.lhs:FAR")
            self.promotes("balance", inputs=[("rhs:FAR", "T4_MAX")])

            # Note that for the following two balances the mult val is set to -1 so that the NET torque is zero
            balance.add_balance("lpt_PR", val=1.5, lower=1.001, upper=8, eq_units="hp", use_mult=True, mult_val=-1)
            self.connect("balance.lpt_PR", "lpt.PR")
            self.connect("lp_shaft.pwr_in_real", "balance.lhs:lpt_PR")
            self.connect("lp_shaft.pwr_out_real", "balance.rhs:lpt_PR")

            balance.add_balance("hpt_PR", val=1.5, lower=1.001, upper=8, eq_units="hp", use_mult=True, mult_val=-1)
            self.connect("balance.hpt_PR", "hpt.PR")
            self.connect("hp_shaft.pwr_in_real", "balance.lhs:hpt_PR")
            self.connect("hp_shaft.pwr_out_real", "balance.rhs:hpt_PR")

        else:

            # In OFF-DESIGN mode we need to redefine the balances:
            #   State Variables:
            #           (W)        Inlet mass flow rate to balance core flow area
            #                      LHS: core_nozz.Throat:stat:area == Area from DESIGN calculation
            #
            #           (FAR)      Fuel-air ratio to balance Thrust req.
            #                      LHS: perf.Fn  == RHS: Thrust requirement (set when TF is instantiated)
            #
            #           (BPR)      Bypass ratio to balance byp. noz. area
            #                      LHS: byp_nozz.Throat:stat:area == Area from DESIGN calculation
            #
            #           (lp_Nmech)   LP spool speed to balance shaft power on the low spool
            #           (hp_Nmech)   HP spool speed to balance shaft power on the high spool

            if self.options["throttle_mode"] == "T4":
                balance.add_balance("FAR", val=0.017, lower=1e-4, eq_units="degR")
                self.connect("balance.FAR", "burner.Fl_I:FAR")
                self.connect("burner.Fl_O:tot:T", "balance.lhs:FAR")
                self.promotes("balance", inputs=[("rhs:FAR", "T4_MAX")])

            elif self.options["throttle_mode"] == "percent_thrust":
                balance.add_balance("FAR", val=0.017, lower=1e-4, eq_units="lbf", use_mult=True)
                self.connect("balance.FAR", "burner.Fl_I:FAR")
                self.connect("perf.Fn", "balance.rhs:FAR")
                self.promotes("balance", inputs=[("mult:FAR", "PC"), ("lhs:FAR", "Fn_max")])

            balance.add_balance("W", units="lbm/s", lower=10.0, upper=1000.0, eq_units="inch**2")
            self.connect("balance.W", "fc.W")
            self.connect("core_nozz.Throat:stat:area", "balance.lhs:W")

            balance.add_balance("BPR", lower=2.0, upper=10.0, eq_units="inch**2")
            self.connect("balance.BPR", "splitter.BPR")
            self.connect("byp_nozz.Throat:stat:area", "balance.lhs:BPR")

            # Again for the following two balances the mult val is set to -1 so that the NET torque is zero
            balance.add_balance(
                "lp_Nmech", val=1.5, units="rpm", lower=500.0, eq_units="hp", use_mult=True, mult_val=-1
            )
            self.connect("balance.lp_Nmech", "LP_Nmech")
            self.connect("lp_shaft.pwr_in_real", "balance.lhs:lp_Nmech")
            self.connect("lp_shaft.pwr_out_real", "balance.rhs:lp_Nmech")

            balance.add_balance(
                "hp_Nmech", val=1.5, units="rpm", lower=500.0, eq_units="hp", use_mult=True, mult_val=-1
            )
            self.connect("balance.hp_Nmech", "HP_Nmech")
            self.connect("hp_shaft.pwr_in_real", "balance.lhs:hp_Nmech")
            self.connect("hp_shaft.pwr_out_real", "balance.rhs:hp_Nmech")

        # Specify the order in which the subsystems are executed:

        self.set_order(
            [
                "balance",
                "fc",
                "inlet",
                "fan",
                "splitter",
                "duct4",
                "lpc",
                "duct6",
                "hpc",
                "bld3",
                "burner",
                "hpt",
                "duct11",
                "lpt",
                "duct13",
                "core_nozz",
                "byp_bld",
                "duct15",
                "byp_nozz",
                "lp_shaft",
                "hp_shaft",
                "perf",
            ]
        )

        # Set up all the engine element flow connections:
        self.connect_flow(cycleData["cycleInfo"]["flow_connections"])

        # Connect bleed flows:
        self.connect_bleeds(cycleData)

        # TODO: Specify solver settings which are hardcoded for now:
        newton = self.nonlinear_solver = om.NewtonSolver()
        newton.options["atol"] = 1e-8

        # set this very small, so it never activates and we rely on atol
        newton.options["rtol"] = 1e-99
        newton.options["iprint"] = 2
        newton.options["maxiter"] = 50
        newton.options["solve_subsystems"] = True
        newton.options["max_sub_solves"] = 1000
        newton.options["reraise_child_analysiserror"] = False
        # ls = newton.linesearch = BoundsEnforceLS()
        ls = newton.linesearch = om.ArmijoGoldsteinLS()
        ls.options["maxiter"] = 3
        ls.options["rho"] = 0.75
        # ls.options['print_bound_enforce'] = True

        self.linear_solver = om.DirectSolver()

        super().setup()
