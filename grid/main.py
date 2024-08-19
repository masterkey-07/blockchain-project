from models.consumer import Consumer
from models.substation import Substation
from models.power_plant import PowerPlant
from models.grid_simulator import GridSimulator
from models.transmission_line import TransmissionLine

TIME_PERIOD = 1/60
M = 1_000_000

plant1 = PowerPlant("Plant 1", 500 * M, TIME_PERIOD)
plant2 = PowerPlant("Plant 2", 700 * M, TIME_PERIOD)

consumers = [
    Consumer("Household A", 50 * M, 100 * M, TIME_PERIOD),
    Consumer("Factory A", 100 * M, 200 * M, TIME_PERIOD)
]

line1 = TransmissionLine("Line 1", 0.05)
line2 = TransmissionLine("Line 2", 0.10)

substation = Substation("Substation 1")

substation.connect_producer(plant1, line1)
substation.connect_producer(plant2, line2)
substation.connect_consumer(consumers[0])
substation.connect_consumer(consumers[1])

simulator = GridSimulator(substations=[substation], producers=[plant1, plant2])

simulator.simulate(1)