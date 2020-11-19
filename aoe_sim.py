from collections import deque
import random as rd
import numpy as np
from villager import Forager
from queue import PriorityQueue

# use an event_heap


class AoeSimulator:
    def __init__(self, running_time):
        self.running_time = running_time
        self.resources = {'wood' : 0 , 'food' : 0, 'gold' : 0, 'stone' : 0}
        self.event_pq = None


    def set_villager_sequence(self, vil_seq : list):
        """
        :param vil_seq: a list of which types of villagers are trained
        e.g [Forager(30), Forager(50), Forager(80), Lumberjack(110)]
        :return:
        """
        self.villager_sequence = vil_seq


    def generate_event_pq(self):
        # convert the villager_production_sequence to a priority queue of events (like resource gathered)
        # form: list of tuple (scheduled_time, resource_type, number)
        # [(40,'food',10), (80,'wood',11), ...]
        event_pq = PriorityQueue()
        if self.villager_sequence:
            for villager in self.villager_sequence:
                t0 = villager.init_time
                tau = villager.work_interval
                tn = self.running_time
                time_list = [t0 + n * tau for n in range((tn - t0)//tau)] # make sure time_list is within the total running time
                for t in time_list:
                    event = (t, villager.resource_type, villager.max_capacity)
                    event_pq.put(event) # priority queue inserts event, smallest time is always at front

            self.event_pq = event_pq
        else:
            print('Please input a villager training sequence.')


    def process_event_pq(self):
        # interpret each item in event_pq
        # event form: [(40,'food',10), (80,'wood',11), ...]
        while not self.event_pq.empty():
            event = self.event_pq.get()
            self.resources[event[1]] += event[2]


    def run(self):
        self.generate_event_pq()
        self.process_event_pq()
        print(self.resources)



if __name__ == '__main__':

    run_time = 500
    sim1 = AoeSimulator(run_time)
    vil_seq = [Forager(10), Forager(25)]
    sim1.set_villager_sequence(vil_seq)
    sim1.run()
