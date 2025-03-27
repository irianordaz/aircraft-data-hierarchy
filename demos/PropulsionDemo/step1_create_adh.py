from utils.generate_demo_adh import generate_test_ADH_propulsion
from utils.ADH_JSON_tools import ADH_to_JSON

output = "output_files/"

adh = generate_test_ADH_propulsion()
ADH_to_JSON(adh,output + "step1_adh.json")
