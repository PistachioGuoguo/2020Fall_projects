from collections import deque
import random as rd
import numpy as np
from villager import Farmer, Lumberjack, GoldMiner, StoneMiner
from queue import PriorityQueue

# use an event_heap

VILLAGE_TRAINING_TIME = 25 # it takes 25 seconds to train a villager
TRY_TRAIN_VILLAGER_INTERVAL = 10 # if not enough food to train villager now, try again after 10 seconds

class AoeSimulator:
    def __init__(self, running_time):
        self.running_time = running_time
        self.resources = {'food': 200, 'wood': 200, 'gold':0, 'stone':0 }
        self.event_heap = None


    def set_villager_sequence(self, vil_seq : list):
        """
        :param vil_seq: a list of which types of villagers are trained
        e.g [Forager(30), Forager(50), Forager(80), Lumberjack(110)]
        :return:
        """
        self.villager_sequence = vil_seq


    def generate_event_heap(self, villager_sequence):
        # convert the villager_production_sequence to a priority queue of events (like resource gathered)
        # form: list of tuple (scheduled_time, resource_type, number)
        # [(40,'food',10), (80,'wood',11), ...]
        event_pq = PriorityQueue()
        if villager_sequence:
            for villager in villager_sequence:
                t0 = villager.init_time
                tau = villager.work_interval
                tn = self.running_time
                time_list = [t0 + n * tau for n in range(1, (tn - t0)//tau)] # make sure time_list is within the total running time
                # also n start from range(1,...) because the first interval cannot gather food
                for t in time_list:
                    event = (t, villager.resource_type, villager.max_capacity)
                    event_pq.put(event) # priority queue inserts event, smallest time is always at front

            return event_pq
        else:
            print('Please input a villager training sequence.')


    def process_event_pq(self, mode='fixed_time'):
        # interpret each item in event_pq
        # event form: [(40,'food',10), (80,'wood',11), ...]
        shortest_time = True if mode == 'shortest_time' else False

        while not self.event_heap.empty():
            event = self.event_heap.get()
            self.resources[event[1]] += event[2]
            if shortest_time: # in shortest_time mode, check whether requirements are met after processing each event
                if self.met_resource_goal():
                    return event[0] # return the time of current event as end time


    def set_resource_goal(self, goal_dict : dict):
        # input the requirement for each kind of resource
        self.resource_goal = goal_dict
        for key in ['food', 'gold', 'wood', 'stone']:
            if key not in goal_dict.keys():
                self.resource_goal[key] = 0


    def met_resource_goal(self):
        # bool function, checking whether current resource have met the goal
        for key in self.resources.keys():
            if self.resources[key] < self.resource_goal[key]: # if any type of resource not met the goal, return False
                return False
        return True


    def run(self, mode='fixed_time'):
        # this a simple mode for test,
        # suits when a complete villager list is fed
        # and no more future add or change of events
        self.event_heap = self.generate_event_heap(self.villager_sequence)
        if mode == 'fixed_time':
            self.process_event_pq() # default mode is fixed_time
            print(self.resources)
        elif mode == 'shortest_time':
            end_time = self.process_event_pq(mode)
            print(self.resources)
            print("Goal achieved in %d sec." % end_time)


    # above is simple version which uses predefined event_heap
    def single_towncenter_sim(self, n_villager=10):
        """
        Dynamically training villager, add to production sequence
        n_villager:  total number of villagers planned to train
        :return:
        """
        init_villagers = [Farmer(0), Farmer(0), Farmer(0)] # each game start with 3 villagers, set them all to farming
        self.labor_division = {'food': 3, 'wood': 0, 'gold': 0, 'stone': 0 } # use a dict to keep track of number of villager in each track
        self.resource_needed = self.resource_goal # temporarily, the needed is goal, but soon needed is >> goal
        # because, e.g, it takes wood to build farm, though wood may not be needed in final goal
        self.event_heap = self.generate_event_heap(init_villagers) # generate event heap for first 3 villagers
        self.event_heap.put((0, 'try_train_villager', 0)) # always start training a villager at beginning
        # event form in event_heap : (time, event_descrpition, amount)

        while not self.event_heap.empty():
            event = self.event_heap.get()
            if event[1] in self.resources.keys(): # if this event related to gathering resouces
                self.resources[event[1]] += event[2]
                if self.met_resource_goal(): # if reached the goal,  return the time of current event as end time
                    self.summary_print(event[0]) # event[0] is current time
                    break
            elif event[1] == 'try_train_villager': # if this is a villager training event
                if self.resources['food'] >= 50 :
                    self.resources['food'] -= 50 # deduct 50 food to start training
                    self.event_heap.put((event[0] + VILLAGE_TRAINING_TIME, 'villager_trained', 0))
                    # after VILLAGER_TRAINING_TIME, a new villager will be produced
                else: # not enough food, wait TRY_AGAIN_VILLAGER_INTERVAL and try again
                    self.event_heap.put((event[0] + TRY_TRAIN_VILLAGER_INTERVAL, 'try_train_villager', 0))
            elif event[1] == 'villager_trained': # a new villager is trained now, assign him/her to a job
                self.clever_assign_new_villager(event[0]) # automatically decide new villager's task, generate its flow, and add to main event_heap
                if sum(self.labor_division.values()) < n_villager: # if current total villagers is less than planned
                    self.event_heap.put((event[0], 'try_train_villager', 0)) # try training new villager

    def summary_print(self, cur_time):
        print("--------------------")
        print(self.resources)
        print("The labor divison: ", end='')
        print(self.labor_division)
        print("Goal achieved in %d sec." % cur_time)



    def clever_assign_new_villager(self, cur_time):
        # return Farmer. Lumberjack,
        # cleverly assign villager to the "most needed place", for example, if food now is relatively enough and
        # wood is in dire need, new villager will be assigned as Lumberjack
        eval_dict = {} # used to evaluate which of the resources is in most need

        for key in self.resources.keys(): # for each type of resource, calculate its needed_score
            goal = self.resource_needed[key]
            current = self.resources[key]
            num_worker = self.labor_division[key]
            if goal == 0:
                eval_dict[key] = 0
            else:
                if num_worker != 0:
                    eval_dict[key] = int((goal - current) / num_worker)
                else:
                    eval_dict[key] = goal - current

        # get most needed type of resource, and create a new villager
        most_needed_resource = max(eval_dict, key=eval_dict.get) # find the resource with largest evaluation score

        new_villager_dict = {'food': Farmer(cur_time), 'wood':Lumberjack(cur_time), 'gold':GoldMiner(cur_time), 'stone':StoneMiner(cur_time)}

        new_villager = new_villager_dict[most_needed_resource]

        temp_event_heap = self.generate_event_heap([new_villager])
        # pour from temp event heap to main event heap

        while not temp_event_heap.empty():
            event = temp_event_heap.get()
            # print(event)
            self.event_heap.put(event)

        self.labor_division[most_needed_resource] += 1


        # print("A new villager is assigned to %s at time %d" % (most_needed_resource, cur_time))



if __name__ == '__main__':


    # single_towncenter
    run_time = 2000 # set an ample amount, will automatically break when goal is met or will not reach the goal
    for n_villager in range(4,30):
        sim1 = AoeSimulator(run_time)
        sim1.set_resource_goal({'food':2000})
        sim1.single_towncenter_sim(n_villager)



# ---------------------------
    # static test version

    # run_time = 1000
    # sim1 = AoeSimulator(run_time)
    # vil_seq = [Farmer(0), Farmer(0), Farmer(0)]
    # sim1.set_villager_sequence(vil_seq)
    # sim1.set_resource_goal({'food':500}) #
    # sim1.run(mode='shortest_time')
