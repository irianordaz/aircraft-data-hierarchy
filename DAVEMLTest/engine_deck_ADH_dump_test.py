from aircraft_data_hierarchy.behaviorLib.propulsion.propulsion_cycle_behavior import EngineDeckCompiled, EngineDeckData
from aviary.utils.named_values import get_items
from aircraft_data_hierarchy.behavior import DAVEfunc, UngriddedTableDef, DataPoint, Function, IndependentVarRef, DependentVarRef
import sys
import os
utils_path = os.path.abspath("/home/mdolabuser/mount/n3cc_demo_packages_npss_boeing_notwate/Aviary/aviary/utils")
if utils_path not in sys.path:
    sys.path.append(utils_path)
from json_data_file import read_json_file
utils_path = os.path.abspath("/home/mdolabuser/mount/n3cc_demo_packages_npss_boeing_notwate/Aviary/aviary/subsystems/propulsion")
if utils_path not in sys.path:
    sys.path.append(utils_path)
from utils import (EngineModelVariables)
import json
import pprint
import numpy as np

MACH = EngineModelVariables.MACH
ALTITUDE = EngineModelVariables.ALTITUDE
THROTTLE = EngineModelVariables.THROTTLE
HYBRID_THROTTLE = EngineModelVariables.HYBRID_THROTTLE
THRUST = EngineModelVariables.THRUST
TAILPIPE_THRUST = EngineModelVariables.TAILPIPE_THRUST
GROSS_THRUST = EngineModelVariables.GROSS_THRUST
SHAFT_POWER = EngineModelVariables.SHAFT_POWER
SHAFT_POWER_CORRECTED = EngineModelVariables.SHAFT_POWER_CORRECTED
RAM_DRAG = EngineModelVariables.RAM_DRAG
FUEL_FLOW = EngineModelVariables.FUEL_FLOW
ELECTRIC_POWER = EngineModelVariables.ELECTRIC_POWER
NOX_RATE = EngineModelVariables.NOX_RATE
TEMPERATURE = EngineModelVariables.TEMPERATURE_ENGINE_T4

aliases = {
    # whitespaces are replaced with underscores converted to lowercase before
    # comparison with keys
    MACH: ['m', 'mn', 'mach', 'mach_number'],
    ALTITUDE: ['altitude', 'alt', 'h'],
    THROTTLE: ['throttle', 'power_code', 'pc'],
    HYBRID_THROTTLE: ['hybrid_throttle', 'hpc', 'hybrid_power_code', 'electric_throttle'],
    THRUST: ['thrust', 'net_thrust'],
    GROSS_THRUST: ['gross_thrust'],
    RAM_DRAG: ['ram_drag'],
    FUEL_FLOW: ['fuel', 'fuel_flow', 'fuel_flow_rate'],
    ELECTRIC_POWER: 'electric_power',
    NOX_RATE: ['nox', 'nox_rate'],
    TEMPERATURE: ['t4', 'temp', 'temperature'],
    SHAFT_POWER: ['shaft_power', 'shp'],
    SHAFT_POWER_CORRECTED: ['shaft_power_corrected', 'shpcor', 'corrected_horsepower'],
    TAILPIPE_THRUST: ['tailpipe_thrust'],
}

def normalize_string(s):
    """
    Normalizes a string by replacing whitespace with underscores and converting to lowercase.
    """
    return s.strip().replace(" ", "_").lower()

def find_canonical_name(candidate):
    """
    Given a normalized candidate string, return the canonical key from aliases if it exists.
    Returns None if no match is found.
    """
    candidate = normalize_string(candidate)
    for canonical, alias_list in aliases.items():
        # Ensure alias_list is iterable.
        if isinstance(alias_list, str):
            alias_list = [alias_list]
        normalized_aliases = [normalize_string(a) for a in alias_list]
        if candidate in normalized_aliases:
            return canonical
    return None

def parse_json_data(json_input):
    """
    Parses a JSON file (or JSON string or dictionary) and returns a consolidated dictionary.

    This function looks for the "ungridded_table_def" section in the JSON and uses its 
    "units" and "data_point" fields for parsing. The resulting dictionary maps each 
    canonical variable (an EngineModelVariables enum member) to a tuple:
        (np.array of values, unit)

    Example output:
        {
            EngineModelVariables.MACH: (array([...]), 'unitless'),
            EngineModelVariables.ALTITUDE: (array([...]), 'ft'),
            ...
        }
    """
    # Load JSON data from file, string, or dict.
    if isinstance(json_input, str):
        try:
            data = json.loads(json_input)
        except json.JSONDecodeError:
            with open(json_input, 'r') as f:
                data = json.load(f)
    elif isinstance(json_input, dict):
        data = json_input
    else:
        raise ValueError("Invalid input. Provide a JSON file path, JSON string, or dictionary.")
    
    # Use the ungridded_table_def section if available.
    if "ungridded_table_def" in data:
        data = data["ungridded_table_def"]

    # Extract the units metadata.
    if "units" in data and isinstance(data["units"], list) and data["units"]:
        units_str = data["units"][0]
        units_list = [u.strip() for u in units_str.split(",")]
    else:
        units_list = []

    # Parse each data point into a list of dictionaries.
    parsed_results = []
    for point in data.get("data_point", []):
        raw_value = point.get("value", "")
        # Split the value string into numbers and the comment containing labels.
        parts = raw_value.split("<!--")
        if len(parts) != 2:
            continue

        values_str = parts[0].strip()
        comment_str = parts[1].replace("-->", "").strip()
        label_list = [lbl.strip() for lbl in comment_str.split(",")]

        try:
            value_list = [float(v) for v in values_str.split()]
        except ValueError:
            continue

        if len(label_list) != len(value_list):
            raise ValueError(f"Mismatch in number of labels ({len(label_list)}) and values ({len(value_list)}).")
        if units_list and (len(units_list) != len(label_list)):
            raise ValueError(f"Mismatch in number of units ({len(units_list)}) and labels ({len(label_list)}).")

        point_dict = {}
        for idx, raw_label in enumerate(label_list):
            normalized_label = normalize_string(raw_label)
            canonical = find_canonical_name(normalized_label)
            if canonical is None:
                continue
            point_dict[canonical] = {
                'value': value_list[idx],
                'unit': units_list[idx] if units_list and idx < len(units_list) else None
            }
        parsed_results.append(point_dict)

    # Consolidate the parsed results:
    # For each variable, collect all values into a list and record the unit.
    consolidated = {}
    for point_dict in parsed_results:
        for key, entry in point_dict.items():
            if key not in consolidated:
                consolidated[key] = {'values': [], 'unit': entry['unit']}
            consolidated[key]['values'].append(entry['value'])

    # Convert lists of values into NumPy arrays and pair with the unit.
    final_result = {}
    for key, v in consolidated.items():
        final_result[key] = (np.array(v['values']), v['unit'])

    return final_result

if __name__ == "__main__":
    engine_table = DAVEfunc(function=[Function(name="Engine Deck")])
    function = engine_table.function[0]

    print(function)

    function.independent_var_ref = [IndependentVarRef(var_id="mn"),
                                    IndependentVarRef(var_id="alt")]
    function.dependent_var_ref = [DependentVarRef(var_id="throttle"),
                                  DependentVarRef(var_id="gross_thrust"),
                                  DependentVarRef(var_id="ram_drag"),
                                  DependentVarRef(var_id="fuel_flow"),
                                  DependentVarRef(var_id="nox_rate")
                                  ]
    # engine_table.function.append(function)

    engine_data = engine_table.ungridded_table_def = UngriddedTableDef()
    data_point_1 = engine_data.data_point = DataPoint(value = "0.0 0.0 21.0 1110.0 0.0 500.3 55.372 <!-- mn, alt, throttle, gross_thrust, ram_drag, fuel_flow, nox_rate-->")
    data_point_2 = engine_data.data_point = DataPoint(value = "0.0 0.0 26.0 4440.1 0.0 964.9 23.442 <!-- mn, alt, throttle, gross_thrust, ram_drag, fuel_flow, nox_rate-->")
    data_point_3 = engine_data.data_point = DataPoint(value = "0.0 0.0 29.0 6660.2 0.0 1368.2 21.499 <!-- mn, alt, throttle, gross_thrust, ram_drag, fuel_flow, nox_rate-->")
    data_point_4 = engine_data.data_point = DataPoint(value = "0.0 0.0 32.0 8880.2 0.0 1790.8 20.979 <!-- mn, alt, throttle, gross_thrust, ram_drag, fuel_flow, nox_rate-->")
    units = "unitless, ft, unitless, lbf, lbf, lb/h, lb/h"

    # data_point_1 = data_point(value = "0.0 0.0 21.0 1110.0 15.0 <!-- mn, alt, throttle, gross_thrust, potato-->")
    # data_point_2 = data_point(value = "0.0 0.0 26.0 4440.1 15.0 <!-- mn, alt, throttle, gross_thrust, potato-->")
    # data_point_3 = data_point(value = "0.0 0.0 29.0 6660.2 15.0 <!-- mn, alt, throttle, gross_thrust, potato-->")
    # data_point_4 = data_point(value = "0.0 0.0 32.0 8880.2 15.0 <!-- mn, alt, throttle, gross_thrust, potato-->")
    # units = "unitless, ft, unitless, lbf, lbf"

    engine_data.data_point = [data_point_1, data_point_2, data_point_3, data_point_4]
    
    engine_data.units = [units]

    with open("/home/mdolabuser/mount/aircraft-data-hierarchy/DAVEMLTest/testing.json", "w") as file:
        file.write(engine_table.model_dump_json(indent=4))
        file.close()

    print(engine_table.model_dump_json(indent=4))

    json_filepath = "/home/mdolabuser/mount/aircraft-data-hierarchy/DAVEMLTest/testing.json"

    result = parse_json_data(json_filepath)

    pprint.pprint(result)

    json_filepath = "/home/mdolabuser/mount/aircraft-data-hierarchy/DAVEMLTest/n3cc_engine_deck.json"

    result = parse_json_data(json_filepath)

    pprint.pprint(result)