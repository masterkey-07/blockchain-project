from time import sleep
from .substation import Substation

class GridSimulator:
    def __init__(self, substations:list[Substation]):
        self.__substations:list[Substation] = substations

    def simulate(self, steps=1, time=0):
        for step in range(steps):
            print(f'Simulated Step {step + 1}')
            
            for substation in self.__substations:
                substation.distribute_power()

                sleep(time)
            
            for substation in self.__substations:
                substation.reset()