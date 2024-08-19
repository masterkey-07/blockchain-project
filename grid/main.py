from models.consumer import Consumer
from models.substation import Substation
from models.power_plant import PowerPlant
from models.grid_simulator import GridSimulator
from models.transmission_line import TransmissionLine

STEPS = 5
TIME_PERIOD = 5/60
M = 1_000_000

# Define Power Plants
plantA = PowerPlant("Plant A", 500 * M, TIME_PERIOD)
plantB = PowerPlant("Plant B", 1200 * M, TIME_PERIOD)
plantC = PowerPlant("Plant C", 500 * M, TIME_PERIOD)

# Define Consumers
factory_a = Consumer("Factory A", 100 * M, 200 * M, TIME_PERIOD)
factory_b = Consumer("Factory B", 100 * M, 200 * M, TIME_PERIOD)

big_factory = Consumer("Big Factory", 400 * M, 800 * M, TIME_PERIOD)

household_a = Consumer("Household A", 50 * M, 100 * M, TIME_PERIOD)
household_b = Consumer("Household B", 50 * M, 100 * M, TIME_PERIOD)
household_c = Consumer("Household C", 50 * M, 100 * M, TIME_PERIOD)
household_d = Consumer("Household D", 50 * M, 100 * M, TIME_PERIOD)

# Define Lines
lineA = TransmissionLine("Line A", 0.06)
lineB = TransmissionLine("Line B", 0.10)
lineC = TransmissionLine("Line C", 0.08)
lineD = TransmissionLine("Line C", 0.12)

# Define Substation A
substationA = Substation("Substation A")
substationA.connect_producer(plantA, lineA)
substationA.connect_producer(plantB, lineB)

substationA.connect_consumer(household_a)
substationA.connect_consumer(household_b)
substationA.connect_consumer(factory_a)
substationA.connect_consumer(big_factory)

# Define Substation B
substationB = Substation("Substation B")
substationB.connect_producer(plantC, lineC)
substationB.connect_producer(plantB, lineB)

substationB.connect_consumer(household_c)
substationB.connect_consumer(household_d)
substationB.connect_consumer(factory_b)
substationB.connect_consumer(big_factory)

# Run Simulation
simulator = GridSimulator(substations=[substationA, substationB])
simulator.simulate(steps=STEPS)