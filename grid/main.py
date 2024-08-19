from models import *

# Create producers
plant1 = PowerPlant("Plant 1", 500)
plant2 = PowerPlant("Plant 2", 700)

# Create transmission lines with loss factors
line1 = TransmissionLine("Line 1", 0.05)  # 5% loss
line2 = TransmissionLine("Line 2", 0.10)  # 10% loss

# Create consumers
consumers = [
    Consumer("Household A", 100),
    Consumer("Household B", 150),
    Consumer("Factory A", 200),
    Consumer("Factory B", 250),
    Consumer("Office A", 300),
    Consumer("Office B", 350)
]

# Create substations and connect producers, transmission lines, and consumers
substation1 = Substation("Substation 1")
substation1.connect_producer(plant1, line1)
substation1.connect_consumer(consumers[0])
substation1.connect_consumer(consumers[1])
substation1.connect_consumer(consumers[2])

substation2 = Substation("Substation 2")
substation2.connect_producer(plant2, line2)
substation2.connect_consumer(consumers[3])
substation2.connect_consumer(consumers[4])
substation2.connect_consumer(consumers[5])

# Create grid control and add substations
grid = GridControl()
grid.add_producer(plant1)
grid.add_producer(plant2)
grid.add_substation(substation1)
grid.add_substation(substation2)

# Balance the grid
grid.balance_power()
