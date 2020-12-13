from villager import Farmer, Lumberjack, GoldMiner, StoneMiner, Builder
from queue import PriorityQueue
from copy import deepcopy
import matplotlib.pyplot as plt
from constants import *


class AoeSimulator:

    def __init__(self, running_time = DEFAULT_RUNNING_TIME):

        self.running_time = running_time
        self.resources = {'food': INITIAL_FOOD, 'wood': INITIAL_WOOD, 'gold':INITIAL_GOLD, 'stone':INITIAL_STONE }
        self.event_heap = None

    def set_villager_sequence(self, villager_sequence : list):
        """
        :param villager_sequence: a list of different work types of Villagers
        e.g [Forager(30), Forager(50), Forager(80), Lumberjack(110)]
        :return:
        """
        self.villager_sequence = villager_sequence

    def generate_event_heap(self, villager_sequence):
        # convert the villager_sequence to a priority queue of events (like resource gathered)
        # format: list of tuple (scheduled_time: int, resource_type(description) : str, amount: int)
        # [(40,'food',10), (80,'wood',11), (100, 'try_train_villager', 0), ...]
        """

        :param villager_sequence: takes the form [Forager(30), Forager(50), Forager(80), Lumberjack(110)]
        :return: a priority queue of events (in form of tuples)
        >>> a1 = AoeSimulator()
        >>> event_heap = a1.generate_event_heap([Farmer(0)])
        >>> event_heap.get()
        (32, 'food', 10)
        >>> event_heap.get()
        (64, 'food', 10)
        >>> event_heap.get()
        (96, 'food', 10)
        >>> event_heap.get()
        (128, 'food', 10)
        """
        event_pq = PriorityQueue()
        if villager_sequence:
            for villager in villager_sequence:
                t0 = villager.init_time
                tau = villager.work_interval
                tn = self.running_time
                if not isinstance(villager, Builder): # for resource collector
                    time_list = [t0 + n * tau for n in range(1, (tn - t0)//tau)] # make sure time_list is within the total running time
                    # also n start from range(1,...) because the first interval cannot gather food
                    for t in time_list:
                        event = (t, villager.resource_type, villager.max_capacity)
                        event_pq.put(event) # priority queue inserts event, smallest time is always at front
                else: # for builder
                    if villager.building_type == 'house':
                        event = (t0 + tau, 'house_completed', 0)
                        event_pq.put(event)

            return event_pq
        else:
            print('Please input a villager training sequence.')

    def process_event_pq(self, mode='fixed_time'):
        # this function is used when testing, and describes the fundamental structure of core function
        # later we expanded different types of events such as 'train_villager', 'build_house' based on this framework
        # interpret each item in event_pq
        # event form: [(40,'food',10), (80,'wood',11), ...]
        """
        >>> a1 = AoeSimulator()
        >>> a1.set_resource_goal({'food':500})
        >>> a1.event_heap = a1.generate_event_heap([Farmer(0), Farmer(0), Farmer(0)])
        >>> a1.process_event_pq(mode='shortest_time')
        320
        >>> a1.process_event_pq()

        :param mode: fixed_time or shortest_time, fixed time run the full designated time and shortest_time will break if met resource goal
        :return: fixed_time return None, shortest_time return int (finish_time),

        """
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
        # boolean function, checking whether current resource have met the goal
        for key in self.resources.keys():
            if self.resources[key] < self.resource_goal[key]: # if any type of resource not met the goal, return False
                return False
        return True

    def run(self, mode='fixed_time'):
        """

        :param mode:
        :return:
        >>> a1 = AoeSimulator()
        >>> a1.set_resource_goal({'food':1000, 'gold':800})
        >>> a1.set_villager_sequence([Farmer(0), Lumberjack(0), GoldMiner(0)])
        >>> a1.run()
        {'food': 3310, 'wood': 4190, 'gold': 3930, 'stone': 0}
        >>> a1 = AoeSimulator()
        >>> a1.set_resource_goal({'food':1000, 'gold':800})
        >>> a1.set_villager_sequence([Farmer(0), Lumberjack(0), Farmer(0)])
        >>> a1.run()
        {'food': 6420, 'wood': 4190, 'gold': 100, 'stone': 0}
        """
        # this a simple mode for execution during test
        # works when a complete villager list is fed, and does not support adding or changing events in future
        self.event_heap = self.generate_event_heap(self.villager_sequence)
        if mode == 'fixed_time': # "fixed-time" mode, will run until the end of event_sequence
            self.process_event_pq() # default mode is fixed_time
            print(self.resources)
        elif mode == 'shortest_time': # "shortest_time" mode, will break when the resource goal is met
            end_time = self.process_event_pq(mode)
            print(self.resources)
            print("Goal achieved in %d sec." % end_time)

    # above is simple version which uses predefined event_heap
    # this is a model of single Town Center without the trivia of building house, farm exhaustion, etc
    def simple_sim(self, num_villager):
        """
        Dynamically training villager and add to production sequence
        n_villager:  total number of villagers planned to train
        :return:
        >>> a1 = AoeSimulator()
        >>> a1.set_resource_goal({'food':500})
        >>> a1.simple_sim(3)
        --------------------
        {'food': 500, 'wood': 200, 'gold': 100, 'stone': 0}
        The labor divison: {'food': 4, 'wood': 0, 'gold': 0, 'stone': 0}
        Goal achieved in 288 sec.
        >>> a2 = AoeSimulator()
        >>> a2.set_resource_goal({'food':1000})
        >>> a2.simple_sim(3)
        --------------------
        {'food': 1000, 'wood': 200, 'gold': 100, 'stone': 0}
        The labor divison: {'food': 4, 'wood': 0, 'gold': 0, 'stone': 0}
        Goal achieved in 704 sec.
        """
        init_villagers = [Farmer(0), Farmer(0), Farmer(0)] # each game start with 3 villagers, set them all to farming
        self.labor_division = {'food': 3, 'wood': 0, 'gold': 0, 'stone': 0 }  # use a dict to keep track of number of villager in each track
        self.resource_needed = self.resource_goal # in this version, resource_needed is just resource_goal
        self.event_heap = self.generate_event_heap(init_villagers) # generate event heap for first 3 villagers
        self.event_heap.put((0, 'try_train_villager', 0)) # always start training a villager at beginning
        # event form in event_heap : (time, event_description, amount)

        while not self.event_heap.empty(): # main event loop
            event = self.event_heap.get()
            event_time, event_desc, event_amount = event  # rename for easier read : time , description and amount

            if event_desc in self.resources.keys(): # if this event related to gathering resources
                self.resources[event_desc] += event_amount
                if self.met_resource_goal(): # if reached the goal,  return the time of current event as end time
                    self.summary_print(event_time)
                    break
            elif event_desc == 'try_train_villager': # if this is a villager training event
                if self.resources['food'] >= FOOD_COST_PER_VILLAGER :
                    self.resources['food'] -= FOOD_COST_PER_VILLAGER # deduct 50 food to start training
                    self.event_heap.put((event_time + VILLAGE_TRAINING_TIME, 'villager_trained', 0))
                    # after VILLAGER_TRAINING_TIME, a new villager will be produced
                else: # not enough food, wait TRY_AGAIN_VILLAGER_INTERVAL and try again
                    self.event_heap.put((event_time + TRY_TRAIN_VILLAGER_INTERVAL, 'try_train_villager', 0))
            elif event_desc == 'villager_trained': # a new villager is trained now, assign him/her to a job
                self.clever_assign_new_villager(event_time) # automatically decide new villager's task, generate its flow, and add to main event_heap
                if sum(self.labor_division.values()) < num_villager: # if current total villagers is less than planned
                    self.event_heap.put((event_time, 'try_train_villager', 0)) # try training new villager


    def clever_assign_new_villager(self, cur_time, consider_housing=False):

        # cleverly assign villager to the "most needed place", for example, if food now is relatively enough and
        # wood is in dire need, new villager will be assigned as Lumberjack
        # consider_housing = True is used in complex_sim

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
        most_needed_resource = max(eval_dict, key=eval_dict.get) # find the resource type with largest evaluation score

        new_villager_dict = {'food': Farmer(cur_time), 'wood':Lumberjack(cur_time), 'gold':GoldMiner(cur_time), 'stone':StoneMiner(cur_time)}

        new_villager = new_villager_dict[most_needed_resource]
        temp_event_heap = self.generate_event_heap([new_villager])

        if consider_housing: # if consider housing, and current pop near its max, override previous allocation
            cur_population = sum(self.labor_division.values())
            # house is the first consideration
            if self.num_accommodation - cur_population == 2 and cur_population >= 8:
                # cur_population >= 8 means not right beginning of game, where we already manually assigned a villager to build house
                temp_event_heap = self.generate_event_heap([Builder(cur_time, 'house')]) # housing if No.1 priority
                self.resources['wood'] -= WOOD_COST_PER_HOUSE # takes 25 wood to build a house
            else: # stick to original allocation
                self.labor_division[most_needed_resource] += 1
                self.resource_needed['wood'] = self.resource_goal['wood'] + self.calc_wood_overhead()  # increase demand for wood
        else:
            self.labor_division[most_needed_resource] += 1
        # pour from temp event heap to main event heap

        while not temp_event_heap.empty():
            event = temp_event_heap.get()
            # print(event)
            self.event_heap.put(event)

        # print("A new villager is assigned to %s at time %d" % (most_needed_resource, cur_time))

    def calc_wood_overhead(self):
        # self-define the wood overhead, since building farm requires wood, we'll later combine this with resource_goal to resource_needed
        return self.labor_division['food'] * WOOD_COST_PER_FARM + 200 # each farm takes 60 wood (one farmer works on one farm), and set 200 for other buildings

    def complex_sim(self, num_villager, return_value=False):
        """
        This version added the requirement of house for population
        also the farm will exhaust "continuously" (automatically deduct 2.5 unit of wood for every 10 unit of food collected)
        Dynamically training villager, add to production sequence
        num_villager:  total number of villagers planned to train
        >>> a1 = AoeSimulator()
        >>> a1.set_resource_goal({'food':1000, 'gold':800})
        >>> a1.complex_sim(10)
        --------------------
        {'food': 1000, 'wood': 535.0, 'gold': 1140, 'stone': 0}
        The labor divison: {'food': 5, 'wood': 2, 'gold': 3, 'stone': 0}
        Goal achieved in 960 sec.

        >>> a1 = AoeSimulator()
        >>> a1.set_resource_goal({'food':1000, 'gold':800})
        >>> a1.complex_sim(15)
        --------------------
        {'food': 1000, 'wood': 687.5, 'gold': 960, 'stone': 0}
        The labor divison: {'food': 8, 'wood': 4, 'gold': 3, 'stone': 0}
        Goal achieved in 800 sec.

        >>> a1 = AoeSimulator()
        >>> a1.set_resource_goal({'food':1000, 'gold':800})
        >>> a1.complex_sim(20)
        --------------------
        {'food': 1000, 'wood': 810.0, 'gold': 930, 'stone': 0}
        The labor divison: {'food': 11, 'wood': 6, 'gold': 3, 'stone': 0}
        Goal achieved in 769 sec.

        """
        self.num_accommodation = INITIAL_ACCOMMO # initiallty a town center can accommodate 5 people
        init_villagers = [Farmer(0), Farmer(0), Builder(0, 'house')] # each game start with 3 villagers, set them all to farming
        self.resources['wood'] -= WOOD_COST_PER_HOUSE # cost for build house at the beginning
        self.labor_division = {'food': 3, 'wood': 0, 'gold': 0, 'stone': 0} # use a dict to keep track of number of villager in each track
        self.resource_needed = deepcopy(self.resource_goal) # temporarily, the needed is goal, but soon needed is >> goal
        # because, e.g, it takes wood to build farm, though wood may not be needed in final goal
        self.event_heap = self.generate_event_heap(init_villagers) # generate event heap for first 3 villagers
        self.event_heap.put((0, 'try_train_villager', 0)) # always start training a villager at beginning
        # event form in event_heap : (time, event_description, amount)

        while not self.event_heap.empty(): # main event loop
            event = self.event_heap.get()
            event_time, event_desc, event_amount = event  # rename for easier read : time , description and amount
            if event_desc in self.resources.keys(): # if this event related to gathering resouces
                self.resources[event_desc] += event_amount
                if event_desc == 'food':
                    self.resources['wood'] -= WOOD_COST_PER_ONE_UNIT_FOOD * event_amount # let's suppose farm takes 1 wood for 4 food
                if self.met_resource_goal(): # if reached the goal,  return the time of current event as end time
                    self.summary_print(event_time) # event[0] is current time
                    if return_value:
                        return event_time
                    break
            elif event_desc == 'try_train_villager': # if this is a villager training event
                if self.resources['food'] >= FOOD_COST_PER_VILLAGER :
                    self.resources['food'] -= FOOD_COST_PER_VILLAGER # deduct 50 food to start training
                    self.event_heap.put((event_time + VILLAGE_TRAINING_TIME, 'villager_trained', 0))
                    # after VILLAGER_TRAINING_TIME, a new villager will be produced
                else: # not enough food, wait TRY_AGAIN_VILLAGER_INTERVAL and try again
                    self.event_heap.put((event_time + TRY_TRAIN_VILLAGER_INTERVAL, 'try_train_villager', 0))
            elif event_desc == 'villager_trained': # a new villager is trained now, assign him/her to a job
                self.clever_assign_new_villager(event_time, consider_housing=True) # automatically decide new villager's task, generate its flow, and add to main event_heap
                if sum(self.labor_division.values()) < num_villager: # if current total villagers is less than planned
                    self.event_heap.put((event_time, 'try_train_villager', 0)) # try training new villager
            elif event_desc == 'house_completed': # indicate a house is done
                self.num_accommodation += ACCOMMO_PER_HOUSE # a house provide 5 accommodation
                self.clever_assign_new_villager(event_time, consider_housing=True)


    def summary_print(self, current_time):
        # You can customize the level of detail of the information you want here
        print("--------------------")
        print(self.resources) # print all resources gathered so far
        print("The labor divison: ", end='')
        print(self.labor_division) # print the allocation of villager to each resources
        print("Goal achieved in %d sec." % current_time)


    def draw_graph(self, resource_goal, num_villager_range: tuple = (5,30)):
        # generate statistical graph for completion time versus the number of villagers

        def generate_graph_title(): # generate title for the graph
            begin = 'The time of generating '
            temp_list = []
            for key in resource_goal:
                if resource_goal[key] != 0:
                    temp_list.append( str(resource_goal[key]) + ' ' + key)
            return begin + ','.join(temp_list)

        low, high = num_villager_range
        time_list = []
        for n_villager in range(low, high + 1):
            sim1 = AoeSimulator()
            sim1.set_resource_goal(resource_goal)
            time_took = sim1.complex_sim(n_villager, return_value=True)
            time_list.append(time_took)

        plt.title(generate_graph_title())
        plt.xlabel('num_villager')
        plt.ylabel('time_spent')
        plt.plot(range(low, high + 1), time_list)
        plt.show()


if __name__ == '__main__':

    min_villager = 10
    max_villager = 100
    resource_goal = {'food': 5000, 'wood':4000, 'gold':4000, 'stone':1500 }
    # resource_goal = {'food':1000, 'gold':800}

    sim1 = AoeSimulator()
    sim1.draw_graph(resource_goal, (min_villager, max_villager))


    # single_towncenter simulation
    # run_time = 2000 # set an ample amount, will automatically break when goal is met or will not reach the goal
    # for n_villager in range(5, 30):
    #     sim1 = AoeSimulator(run_time)
    #     sim1.set_resource_goal({'food':500})
    #     # sim1.simple_sim(n_villager)
    #     sim1.complex_sim(n_villager)


# ---------------------------
    # static test version

    # run_time = 1000
    # sim1 = AoeSimulator(run_time)
    # vil_seq = [Farmer(0), Farmer(0), Farmer(0)]
    # sim1.set_villager_sequence(vil_seq)
    # sim1.set_resource_goal({'food':500}) #
    # sim1.run(mode='shortest_time')
