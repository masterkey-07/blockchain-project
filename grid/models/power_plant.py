class PowerPlant:
    def __init__(self, name:str, max_output:int, time_period:int=1):
        self.__name = name
        self.__max_output = max_output
        self.__time_period = time_period
        self.__current_output = 0

    def get_max_output(self):
        return round(self.__max_output * self.__time_period)

    def get_available_output(self):
        max_output = self.get_max_output()
        
        if max(max_output - self.__current_output, 0) == 0:
            return 0
        
        return max_output - self.__current_output

    def reset(self):
        self.__current_output = 0

    def request_power(self, requested_output:int):
        max_output = self.get_max_output()

        provided_power = min(requested_output, max_output - self.__current_output)

        self.__current_output += provided_power

        print(f'Producer {self.__name} generated {provided_power} Wh')

        return provided_power