import aoe_sim
from villager import Farmer, Lumberjack, GoldMiner

a1 = aoe_sim.AoeSimulator()
a1.set_resource_goal({'food':1000, 'gold':800})
a1.set_villager_sequence([Farmer(0), Lumberjack(0), Farmer(0)])
a1.run()

# event_heap = a1.generate_event_heap([Farmer(0)])
# print(event_heap.get())