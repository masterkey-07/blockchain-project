import math
from .consumer import Consumer
from .power_plant import PowerPlant
from .transmission_line import TransmissionLine

type producer_line = tuple[PowerPlant, TransmissionLine]

class Substation:
    def __init__(self, name:str):
        self.__name = name
        self.__connected_producers:list[producer_line] = []
        self.__connected_consumers:list[Consumer] = []

    def connect_producer(self, producer:PowerPlant, transmission_line:TransmissionLine):
        self.__connected_producers.append((producer, transmission_line))

    def connect_consumer(self, consumer:Consumer):
        consumer.connect_to_substation(self)

        self.__connected_consumers.append(consumer)

    def reset(self):
        for producer in self.__connected_producers:
            producer[0].reset()

        for consumer in self.__connected_consumers:
            consumer.reset()

    def distribute_power(self):
        print(f"Substation {self.__name} started the distribution")

        available_capacity = sum(producer.get_available_output() for producer, _ in self.__connected_producers)
        
        if available_capacity == 0:
            raise Exception("There is no Power Capacity!")

        total_demand = sum(consumer.get_demand() for consumer in self.__connected_consumers)

        if total_demand == 0:
            raise Exception("There is no Demand!")
        
        total_power = 0

        for producer, line in self.__connected_producers:
            proportional_request = (producer.get_available_output() / available_capacity) * total_demand

            loss_factor = line.get_loss_factor()

            generated_power = producer.request_power(math.ceil(proportional_request * (1 + loss_factor)))

            transmitted_power = line.transmit(generated_power)

            total_power += transmitted_power

        for consumer in self.__connected_consumers:
            proportion = consumer.get_demand() / total_demand
            
            consumer.consume_power(math.floor(total_power * proportion))
