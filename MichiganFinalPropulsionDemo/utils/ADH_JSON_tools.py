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
    with open(path, "w") as file:
        file.write(ADHInstance.model_dump_json(indent=4,exclude_unset=exclude_unset,exclude_defaults=exclude_defaults))
        file.close()

def JSON_to_ADH(path,ADHInstance):
    """
    Reads and validates a JSON file against an existing ADHInstance. Updates the ADHInstance with data from the JSON and returns it.
    """

    # Open and read the JSON file
    with open(path, 'r') as file:
        adhData = json.load(file)

    # Convert read new ADH JSON to string
    adhData = json.dumps(adhData)
    
    # Read in the new ADH
    ADHInstanceNew = ADHInstance.model_validate_json(adhData)

    return ADHInstanceNew