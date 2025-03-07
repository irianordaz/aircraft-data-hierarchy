import json
import os
from aircraft_data_hierarchy.behavior import DAVEfunc, UngriddedTableDef, DataPoint, IndependentVarRef, DependentVarRef, Function, FileHeader


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


def initialize_engine_deck_ADH(prob, ADHInstance, deck_name = "Engine Deck", promoted_names=None, ordered_keys=["mn", "alt", "throttle", "gross_thrust", "ram_drag", "fuel_flow", "nox_rate"]):
    """
    Initializes a new engine deck in the ADH propulsion behavior branch in DaveML format. 
    The function appends a new deck if there are existing decks and returns the index associated with the added deck.
    The function intializes the DaveML structure, independent variables, dependent variables, and the units.

    The canonical order (and comment order) is:
         "mn, alt, throttle, gross_thrust, ram_drag, fuel_flow, nox_rate"

    Parameters:
      prob         : OpenMDAO problem instance.
      ADHInstance: ADHInstance pydantic object
      deck_name: The name of the engine deck to differentiate it from others
      promoted_names (dict, optional): Mapping from canonical variable names to promoted names.
            Default values (adjust these as needed) are used if not provided.
    """

    #Add Engine Deck to ADH
    if ADHInstance.behavior.engine_decks == None:
        ADHInstance.behavior.engine_decks = []
        ADHInstance.behavior.engine_decks.append(DAVEfunc(function=[Function(name=f"{deck_name} Header")],ungridded_table_def=[UngriddedTableDef(name=f"{deck_name} Data")]))
    else:
        ADHInstance.behavior.engine_decks.append(DAVEfunc(function=[Function(name=f"{deck_name} Header")],ungridded_table_def=[UngriddedTableDef(name=f"{deck_name} Data")]))

    # The engine deck's index -accounts for multiple engine decks in the same ADH
    deck_index = len(ADHInstance.behavior.engine_decks) - 1

    ADHInstance.behavior.engine_decks[deck_index].file_header = FileHeader(name=deck_name)
    
    function = ADHInstance.behavior.engine_decks[deck_index].function[0]
    engine_data = ADHInstance.behavior.engine_decks[deck_index].ungridded_table_def[0] 

    independent_vars = []
    dependent_vars = []
    for alias in ordered_keys:
        if alias in ["mn", "alt", "throttle", "hybrid_throttle"]:
            independent_vars.append(IndependentVarRef(var_id=alias))
        else:
            dependent_vars.append(DependentVarRef(var_id=alias))

    function.independent_var_ref = independent_vars
    function.dependent_var_ref = dependent_vars

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

    #Units 
    units_list = []
    for key in ordered_keys:
        prom_key = promoted_names.get(key)
        unit = get_unit(prob, prom_key)
        units_list.append(unit)
    units_string = ", ".join(units_list)
    engine_data.units = [units_string]

    print(f"Initialized Deck {deck_index}")

    return deck_index



def append_data_point_ADH(prob, engine_data, promoted_names=None, ordered_keys=["mn", "alt", "throttle", "gross_thrust", "ram_drag", "fuel_flow", "nox_rate"]):
    """
    Retrieves key variables from an OpenMDAO problem instance using prob.get_val and appends
    a new data point to the ungridded_table_def from an ADH instance.

    The canonical order (and comment order) is:
         "mn, alt, throttle, gross_thrust, ram_drag, fuel_flow, nox_rate"

    Parameters:
      prob         : OpenMDAO problem instance.
      engine_data: UngriddedTableDef instance from the ADH
      promoted_names (dict, optional): Mapping from canonical variable names to promoted names.
            Default values (adjust these as needed) are used if not provided.
    """

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

    # add to ADH Instance

    if engine_data.data_point == None:
        engine_data.data_point = []
        engine_data.data_point.append(DataPoint(value=full_value_str))
    else:
        engine_data.data_point.append(DataPoint(value=full_value_str))
    
    print(f"Appended new data point to ADH Instance")


def append_data_point_json(prob, json_filepath, promoted_names=None, ordered_keys=["mn", "alt", "throttle", "gross_thrust", "ram_drag", "fuel_flow", "nox_rate"]):
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