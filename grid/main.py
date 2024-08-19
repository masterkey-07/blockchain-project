from models.consumer import Consumer
from models.substation import Substation
from models.power_plant import PowerPlant
from models.grid_simulator import GridSimulator
from models.transmission_line import TransmissionLine

STEPS = 50
M = 1_000_000
TIME_PERIOD = 5/60

# Define Power Plants
plantA = PowerPlant(name="Plant A", max_output=500 * M, time_period=TIME_PERIOD, account="0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d")
plantA.authorize()

plantB = PowerPlant(name="Plant B",max_output= 1200 * M,time_period= TIME_PERIOD, account="0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a")
plantB.authorize()

plantC = PowerPlant(name="Plant C",max_output= 500 * M,time_period= TIME_PERIOD, account="0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6")
plantC.authorize()

# Define Consumers

factory_a = Consumer("Factory A", 100 * M, 200 * M, "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a", TIME_PERIOD)
factory_a.authorize()

factory_b = Consumer("Factory B", 100 * M, 200 * M, "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",TIME_PERIOD)
factory_b.authorize()

big_factory = Consumer("Big Factory", 400 * M, 800 * M, "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e",TIME_PERIOD)
big_factory.authorize()

household_a = Consumer("Household A", 50 * M, 100 * M, "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",TIME_PERIOD)
household_a.authorize()

household_b = Consumer("Household B", 50 * M, 100 * M, "0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97",TIME_PERIOD)
household_b.authorize()

household_c = Consumer("Household C", 50 * M, 100 * M, "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6",TIME_PERIOD)
household_c.authorize()

household_d = Consumer("Household D", 50 * M, 100 * M, "0xf214f2b2cd398c806f84e317254e0f0b801d0643303237d97a22a48e01628897",TIME_PERIOD)
household_d.authorize()

# Define Lines
lineA = TransmissionLine("Line A", account="0x701b615bbdfb9de65240bc28bd21bbc0d996645a3dd57e7b12bc2bdf6f192c82")
lineA.authorize()

lineB = TransmissionLine("Line B", account="0xa267530f49f8280200edf313ee7af6b827f2a8bce2897751d06a843f644967b1")
lineB.authorize()

lineC = TransmissionLine("Line C", account="0x47c99abed3324a2707c28affff1267e45918ec8c3f20b8aa892e8b065d2942dd")
lineC.authorize()

lineD = TransmissionLine("Line C", account="0xc526ee95bf44d8fc405a158bb884d9d1238d99f0612e9f33d006bb0789009aaa")
lineD.authorize()


# Define Substation A
substationA = Substation("Substation A", account="0x8166f546bab6da521a8369cab06c5d2b9e46670292d85c875ee9ec20e84ffb61")
substationA.authorize()
substationA.connect_producer(plantA, lineA)
substationA.connect_producer(plantB, lineB)

substationA.connect_consumer(household_a)
substationA.connect_consumer(household_b)
substationA.connect_consumer(factory_a)
substationA.connect_consumer(big_factory)

# Define Substation B
substationB = Substation("Substation B", account="0xea6c44ac03bff858b476bba40716402b03e41b8e97e276d1baec7c37d42484a0")
substationB.authorize()
substationB.connect_producer(plantC, lineC)
substationB.connect_producer(plantB, lineB)

substationB.connect_consumer(household_c)
substationB.connect_consumer(household_d)
substationB.connect_consumer(factory_b)

substationB.connect_consumer(big_factory)

# Run Simulation
simulator = GridSimulator(substations=[substationA, substationB])
simulator.simulate(steps=STEPS, time=1)