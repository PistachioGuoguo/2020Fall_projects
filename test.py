import numpy as np
import random as rd
from queue import PriorityQueue


pq1 = PriorityQueue()

pq1.put(2)
pq1.put(3)
pq1.put(4)
pq1.put(1)

print(pq1.get())
print(pq1.get())
