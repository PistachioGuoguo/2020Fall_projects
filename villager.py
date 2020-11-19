import random as rd




class Villager:
    def __init__(self, init_time): #
        self.init_time = init_time
        self.max_capacity = 10 # take 10 unit of capacity maximum
        self.work_interval = 10 # resource reach max every 10s
        self.resource_type = None



class Forager(Villager):
    def __init__(self, init_time):
        super().__init__(init_time)
        self.resource_type= 'food' # the resource type a forager collects is wood

