import simpy
from simulation import ParkingSimulation

print("---MEMULAI SIMULASI PARKIR UPI---")

env = simpy.Environment()

sim = ParkingSimulation(env)

sim.start()

env.run(until=30)

print("---SIMULASI SELESAI---")
