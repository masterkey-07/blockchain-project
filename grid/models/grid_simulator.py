from .substation import Substation
from .power_plant import PowerPlant

class GridSimulator:
    def __init__(self, substations:list[Substation], producers:list[PowerPlant]):
        
        self.__producers:list[PowerPlant] = producers
        self.__substations:list[Substation] = substations

    def simulate(self, steps=1):
        for step in range(steps):
            print(f'Simulated Step {step + 1}')
            
            for substation in self.__substations:
                substation.distribute_power()
            
            for producer in self.__producers:
                producer.reset()