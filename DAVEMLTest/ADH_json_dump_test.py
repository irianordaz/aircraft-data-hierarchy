import json
from utils.generate_demo_adh import generate_test_ADH_propulsion

#Generate Test ADH
adh = generate_test_ADH_propulsion()
adh.model_rebuild()

#Dump to JSON 
with open("/home/mdolabuser/mount/aircraft-data-hierarchy/DAVEMLTest/output_files/adh_in.json", "w") as file:
    file.write(adh.model_dump_json(indent=4,exclude_unset=True,exclude_defaults=False))
    file.close()


# Open and read the JSON file
with open("/home/mdolabuser/mount/aircraft-data-hierarchy/DAVEMLTest/output_files/adh_in.json", 'r') as file:
    adhNewData = json.load(file)

# Simulate a change
adhNewData["name"] = "Engine MOD"

# Convert read new ADH JSON to string
adhNewData = json.dumps(adhNewData)
 
# Read in the new ADH
adhNEW = adh.model_validate_json(adhNewData)

# Output new ADH
print(adhNEW.model_dump_json(indent=4,exclude_unset=True,exclude_defaults=False))