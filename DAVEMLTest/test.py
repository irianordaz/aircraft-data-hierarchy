#from typing import List, Optional
#from pydantic import Field, field_validator
from aircraft_data_hierarchy.behaviorLib.propulsion.propulsion_cycle_behavior import EngineDeckCompiled, EngineDeckData
#from aircraft_data_hierarchy.work_breakdown_structure.propulsion.propulsion_cycle import PropulsionCycle
#import json

if __name__ == "__main__":
    engine_data = EngineDeckCompiled()
    data_point_1 = EngineDeckData(mn = 0.0, alt = 0.0, throttle = 21.0, 
                                gross_thrust = 1110.0, ram_drag = 0.0, 
                                fuel_flow = 500.3, nox_rate = 55.372)
    data_point_2 = EngineDeckData(mn = 0.0, alt = 0.0, throttle = 26.0, 
                                gross_thrust = 4440.1, ram_drag = 0.0, 
                                fuel_flow = 964.9, nox_rate = 23.442)
    engine_data.flight_cond = [data_point_1, data_point_2]

    with open("/home/mdolabuser/mount/aircraft-data-hierarchy/DAVEMLTest/testing.json", "w") as file:
        file.write(engine_data.model_dump_json(indent=4))
        file.close()

    print(engine_data.model_dump_json(indent=4))

