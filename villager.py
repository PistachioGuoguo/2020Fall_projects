import random as rd


# the reference data of AOE gather speed: https://ageofempires.fandom.com/wiki/Villager_(Age_of_Empires_II)

class Villager:
    def __init__(self, init_time): #
        self.init_time = init_time
        self.max_capacity = 10 # take 10 unit of capacity maximum
        self.resource_type = None


class Farmer(Villager):
    # for simplicity, Forager, Fisherman, Shepherd, Hunter are all combined into farmer for now
    def __init__(self, init_time):
        super().__init__(init_time)
        self.resource_type= 'food'
        self.work_interval = 32 # resource reach max every 32.2 s


class Lumberjack(Villager):
    def __init__(self, init_time):
        super().__init__(init_time)
        self.resource_type= 'wood'
        self.work_interval = 25


class GoldMiner(Villager):
    def __init__(self, init_time):
        super().__init__(init_time)
        self.resource_type= 'gold'
        self.work_interval = 26


class StoneMiner(Villager):
    def __init__(self, init_time):
        super().__init__(init_time)
        self.resource_type= 'stone'
        self.work_interval = 27