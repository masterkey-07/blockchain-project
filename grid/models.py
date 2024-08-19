class PowerPlant:
    def __init__(self, name, max_output):
        self.name = name
        self.max_output = max_output
        self.current_output = 0

    def generate_power(self, demand):
        self.current_output = min(demand, self.max_output)
        return self.current_output

class Consumer:
    def __init__(self, name, demand):
        self.name = name
        self.demand = demand
        self.received_power = 0

    def consume_power(self, power):
        self.received_power = min(power, self.demand)
        print(f"{self.name} received {self.received_power}MW")

class TransmissionLine:
    def __init__(self, name, loss_factor):
        self.name = name
        self.loss_factor = loss_factor

    def transmit(self, power):
        transmitted_power = power * (1 - self.loss_factor)
        print(f"{self.name} transmitted {transmitted_power}MW with a loss factor of {self.loss_factor}")
        return transmitted_power

class Substation:
    def __init__(self, name):
        self.name = name
        self.connected_producers = []
        self.connected_consumers = []
        self.connected_lines = []

    def connect_producer(self, producer, transmission_line):
        self.connected_producers.append((producer, transmission_line))

    def connect_consumer(self, consumer):
        self.connected_consumers.append(consumer)

    def distribute_power(self):
        total_power = 0
        for producer, line in self.connected_producers:
            generated_power = producer.generate_power(sum([consumer.demand for consumer in self.connected_consumers]))
            transmitted_power = line.transmit(generated_power)
            total_power += transmitted_power

        power_per_consumer = total_power / len(self.connected_consumers)
        
        for consumer in self.connected_consumers:
            consumer.consume_power(power_per_consumer)

# class GridControl:
#     def __init__(self):
#         self.producers = []
#         self.substations = []

#     def add_producer(self, producer):
#         self.producers.append(producer)

#     def add_substation(self, substation):
#         self.substations.append(substation)

#     def balance_power(self):
#         for substation in self.substations:
#             substation.distribute_power()

