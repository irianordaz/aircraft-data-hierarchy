import json


def ADH_to_JSON(ADHInstance, path, exclude_unset=True, exclude_defaults=False):
    """
    Outputs an ADHInstance to JSON at specified path

    ADHInstance: 
    pydantic ADH instance

    path: str
    complete path to the json file include the .json extension

    exclude_unset: bool
    excludes unset fields

    exclude_defaults: bool
    excludes default values

     """
    
    ADHJSON = ADHInstance.model_dump_json(indent=4,exclude_unset=exclude_unset,exclude_defaults=exclude_defaults)
    ADHJSONDict = json.loads(ADHJSON)
    ADHJSONON = json.dumps({"OuterNest":ADHJSONDict}, indent=4)
    with open(path, "w") as file:
        file.write(ADHJSONON)
        file.close()

def JSON_to_ADH(path,ADHInstance):
    """
    Reads and validates a JSON file against an existing ADHInstance. Updates the ADHInstance with data from the JSON and returns it.
    """

    # Open and read the JSON file
    with open(path, 'r') as file:
        adhData = json.load(file)

    # Convert read new ADH JSON to string
    adhData = json.dumps(adhData["OuterNest"])
    
    # Read in the new ADH
    ADHInstanceNew = ADHInstance.model_validate_json(adhData)

    return ADHInstanceNew

def ADH_to_Engine_Deck(input_path, output_path):
    """
    Extracts the 'engine_decks' data from an existing ADH JSON file and saves it separately.

    input_path: str
        The path to the existing ADH.json file.

    output_path: str
        The path where the extracted engine_decks JSON should be saved.
    """

    # Read the ADH JSON file
    with open(input_path, "r") as file:
        adh_data = json.load(file)  # Load as dictionary

    # Check if "engine_decks" exists in the JSON data
    if "engine_decks" in adh_data["OuterNest"]["behavior"]:
        engine_decks_data = adh_data["OuterNest"]["behavior"]["engine_decks"][0]  # Extract only engine_decks

        # Convert extracted data to formatted JSON string
        engine_decks_json = json.dumps(engine_decks_data, indent=4)

        # Save the extracted data to the output file
        with open(output_path, "w") as file:
            file.write(engine_decks_json)
    else:
        raise KeyError("The input JSON file does not contain 'engine_decks'.")
