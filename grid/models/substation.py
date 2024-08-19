import math
from .consumer import Consumer
from .power_plant import PowerPlant
from .transmission_line import TransmissionLine

type producer_line = tuple[PowerPlant, TransmissionLine]

class Substation:
    def __init__(self, name:str):
        self.name = name
        self.connected_producers:list[producer_line] = []
        self.connected_consumers:list[Consumer] = []
        self.connected_lines:list[TransmissionLine] = []

    def connect_producer(self, producer:PowerPlant, transmission_line:TransmissionLine):
        self.connected_producers.append((producer, transmission_line))

    def connect_consumer(self, consumer:Consumer):
        self.connected_consumers.append(consumer)

    def distribute_power(self):
        total_capacity = sum(producer.get_max_output() for producer, _ in self.connected_producers)
        
        if total_capacity == 0:
            raise("There is no Power Capacity!")

        total_demand = sum(consumer.get_new_demand() for consumer in self.connected_consumers)

        if total_demand == 0:
            raise("There is no Demand!")
        
        total_power = 0

        for producer, line in self.connected_producers:
            proportional_request = (producer.get_max_output() / total_capacity) * total_demand

            loss_factor = line.get_loss_factor()

            generated_power = producer.request_power(math.ceil(proportional_request * (1 + loss_factor)))

            transmitted_power = line.transmit(generated_power)

            total_power += transmitted_power

        for consumer in self.connected_consumers:
            proportion = consumer.get_current_demand() / total_demand
            
            consumer.consume_power(math.floor(total_power * proportion))
