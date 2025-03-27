from utils.ADH_JSON_tools import JSON_to_ADH, ADH_to_JSON, ADH_to_Engine_Deck

output = "output_files/"

ADH_to_Engine_Deck(output + "step5_adh.json", output + "engine_deck_for_Aviary.json")