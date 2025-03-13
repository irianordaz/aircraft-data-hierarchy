import json
from utils.generate_demo_adh import generate_test_ADH_propulsion

adh = generate_test_ADH_propulsion()
adh.model_rebuild()


with open("/home/mdolabuser/mount/aircraft-data-hierarchy/DAVEMLTest/output_files/adh_in.json", "w") as file:
    file.write(adh.model_dump_json(indent=4))
    file.close()