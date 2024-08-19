import random

class Consumer:
    def __init__(self, name: str, min_demand: float, max_demand: float, time_period: int = 1):
        self.__name = name
        self.__substations:set = set()
        self.__min_demand = min_demand
        self.__max_demand = max_demand
        self.__time_period = time_period
        
        self.__current_demand:int = None

    def reset(self):
        self.__current_demand = None

    def connect_to_substation(self, substation):
        self.__substations.add(substation)

    def get_quantity_of_substations(self):
        return len(self.__substations)

    def __get_new_demand(self):
        random_demand = random.uniform(self.__min_demand, self.__max_demand)

        return round(random_demand * self.__time_period)
    
    def get_demand(self) -> float:
        if (self.__current_demand is None):
            self.__current_demand = self.__get_new_demand()
            return self.__current_demand
        
        return self.__current_demand / len(self.__substations)
        
    def consume_power(self, received: int):
        print(f"{self.__name} received {received} of {self.get_demand()} Wh")
