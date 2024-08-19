import random

class Consumer:
    def __init__(self, name: str, min_demand: float, max_demand: float, time_period: int = 1):
        self.__name = name
        
        self.__min_demand = min_demand
        self.__max_demand = max_demand

        self.__time_period = time_period
        
        self.__current_demand:int = None

    def get_new_demand(self) -> float:
        random_demand = random.uniform(self.__min_demand, self.__max_demand)

        self.__current_demand = round(random_demand * self.__time_period)

        return self.__current_demand

    def get_current_demand(self) -> float:
        return self.__current_demand

    def consume_power(self, received: float):
        print(f"{self.__name} received {received} of {self.get_current_demand()} Wh")
