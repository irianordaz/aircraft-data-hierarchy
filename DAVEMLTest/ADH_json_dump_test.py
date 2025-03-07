import json
from generate_demo_adh import generate_test_ADH_propulsion

adh = generate_test_ADH_propulsion()
adh.model_rebuild()
adhjson = adh.model_dump()

with open('adh_in_new.json', 'w') as j:
    json.dump(adhjson, j, indent=4)