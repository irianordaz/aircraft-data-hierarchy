import json

def parse_deck_file_to_json(input_deck_path, output_json_path):
    """
    Parses a .deck file with a table of data into the JSON format expected by the system.
    
    The deck file is expected to have extraneous lines before the table header.
    The header is identified as the first line containing both "(" and ")" and a comma.
    
    The header should be in the format:
    
      Mach_Number (unitless), Altitude (ft), Throttle (unitless), Gross_Thrust (lbf), 
      Ram_Drag (lbf), Fuel_Flow (lb/h), NOx_Rate (lb/h)
    
    This function:
      - Extracts the variable names and units from the header.
      - Uses a preferred alias mapping (e.g. "Mach_Number" becomes "mn").
      - Processes each subsequent data row into a space‐separated string of values with an appended 
        HTML comment listing the preferred aliases.
      - Builds the "ungridded_table_def" section using the extracted units and data points.
      - Creates a "function" section in which "mn" and "alt" are set as the independent variables,
        and all other variables are the dependent variables.
    
    Parameters:
      input_deck_path (str): Path to the input .deck file.
      output_json_path (str): Path to write the output JSON.
    """
    # Mapping from normalized header names to preferred alias.
    preferred_aliases = {
        "mach_number": "mn",
        "altitude": "alt",
        "throttle": "throttle",
        "gross_thrust": "gross_thrust",
        "ram_drag": "ram_drag",
        "fuel_flow": "fuel_flow",
        "nox_rate": "nox_rate"
    }
    
    # Read all lines from the deck file.
    with open(input_deck_path, 'r') as f:
        all_lines = [line.strip() for line in f.readlines() if line.strip()]
    
    if not all_lines:
        raise ValueError("Deck file is empty or contains only whitespace.")
    
    # --- Find the Header ---
    header_line = None
    header_index = None
    for idx, line in enumerate(all_lines):
        # Look for a line that contains both "(" and ")" and at least one comma.
        if "(" in line and ")" in line and "," in line:
            header_line = line
            header_index = idx
            break
    if header_line is None:
        raise ValueError("No header line found in the deck file.")
    
    # --- Parse the Header ---
    # Split header on commas.
    header_cols = [col.strip() for col in header_line.split(",")]
    
    header_vars = []    # normalized variable names
    header_units = []   # corresponding units
    alias_list = []     # preferred aliases to be appended as comment
    
    for col in header_cols:
        # Expect format: "VariableName (unit)".
        if "(" in col and ")" in col:
            var_part, rest = col.split("(", 1)
            unit = rest.split(")")[0].strip()
            var_name = var_part.strip()
        else:
            var_name = col
            unit = ""
        norm_var = var_name.lower()
        header_vars.append(norm_var)
        header_units.append(unit)
        alias = preferred_aliases.get(norm_var, norm_var)
        alias_list.append(alias)
    
    # Create the units string for the JSON.
    units_string = ", ".join(header_units)
    
    # --- Process Data Rows ---
    # Process only lines after the header line.
    data_points = []
    for line in all_lines[header_index+1:]:
        # Skip lines that exactly match the header.
        if line == header_line:
            continue
        # Split the row on commas.
        values = [val.strip() for val in line.split(",") if val.strip()]
        if len(values) != len(header_vars):
            raise ValueError("Mismatch between number of header columns and data values in row:\n" + line)
        # Join values with a space.
        values_str = " ".join(values)
        # Append an HTML comment with the alias list.
        comment_str = " <!-- " + ", ".join(alias_list) + " -->"
        full_value_str = values_str + comment_str
        
        data_points.append({
            "mod_id": None,
            "value": full_value_str
        })
    
    # --- Build Function Section ---
    # Mach Number ("mn") and Altitude ("alt") are the independent variables.
    independent_vars = []
    dependent_vars = []
    for alias in alias_list:
        if alias in ["mn", "alt"]:
            independent_vars.append({
                "var_id": alias,
                "min": None,
                "max": None,
                "extrapolate": None,
                "interpolate": None
            })
        else:
            dependent_vars.append({"var_id": alias})
    
    function_section = [{
        "name": "Engine Deck",
        "description": None,
        "provenance": None,
        "provenance_ref": None,
        "independent_var_pts": None,
        "dependent_var_pts": None,
        "independent_var_ref": independent_vars,
        "dependent_var_ref": dependent_vars,
        "function_defn": None
    }]
    
    # --- Build Final JSON Structure ---
    final_json = {
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
            "data_point": data_points
        },
        "function": function_section,
        "check_data": None
    }
    
    # Write the final JSON to the output file.
    with open(output_json_path, 'w') as outfile:
        json.dump(final_json, outfile, indent=4)
    
    print(f"Converted deck file '{input_deck_path}' to JSON file '{output_json_path}'.")

if __name__ == "__main__":
    input_deck = "/home/mdolabuser/mount/n3cc_demo_packages_npss_boeing_notwate/Aviary/aviary/models/engines/turbofan_22k.deck"   # path to your .deck file
    output_json = "/home/mdolabuser/mount/aircraft-data-hierarchy/DAVEMLTest/n3cc_engine_deck.json"  # path for the output JSON file
    parse_deck_file_to_json(input_deck, output_json)
