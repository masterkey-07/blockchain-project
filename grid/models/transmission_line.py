import math
import random

class TransmissionLine:
    def __init__(self, name:str, loss_factor:float):
        self.__name = name
        self.__loss_factor = loss_factor

    def get_loss_factor(self):
        return self.__loss_factor

    def transmit(self, power:int):
        loss = round(random.uniform(0.01, self.__loss_factor), 2)
        
        transmitted_power = math.floor(power * (1 - self.__loss_factor))
        
        print(f"{self.__name} transmitted {transmitted_power} Wh with a loss factor of {loss}")
        
        return transmitted_power

