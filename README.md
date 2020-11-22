# AoE2 Resource Gathering Simulator - IS597 PRO 2020 Fall project

Author: Zizhou Sang ([zsang2@illinois.edu](mailto:zsang2@illinois.edu))


## Introduction

*Age of Empires 2* is a classic real-time strategy game developed by Ensemble Studios as early in 1998. Since childhood, I have been wondering what villager allocation strategy can provide sufficient resources for any requirements in shortest time.

For more information of this project, please see [my deck at Goold Drive](https://drive.google.com/file/d/1vWRWCLP4rZqXWW97KSKySzxAEAmWBfZi/view?usp=sharing). Thanks!

## Usage

1\) Draw statistical graph for the time of setting different numbers of villagers to complete a specific resource goal:

```python
if __name__ == '__main__':

    min_villager = 10 
    max_villager = 100 
    resource_goal = {'food': 5000, 'wood':4000, 'gold':4000, 'stone':1500 }

    sim1 = AoeSimulator()
    sim1.draw_graph(resource_goal, (min_villager, max_villager))
```

2\)  ```complex_sim()``` is the version where houses must to be built to accommodate current population,  also for every food gathered, we will automatically deduct some wood (which we try to make it proportional to the cost of farm). On the other hand,  ```simple_sim()``` does not need to build house, and gathering food have no effects on wood. In both versions, the only parameter we need to set is ```num_villager```. The *Town Center* will keep trying to train villagers until the number is equal to the parameter ```num_villager```.

```python
# single_towncenter simulation
for n_villager in range(5, 30):
    sim1 = AoeSimulator(run_time)
    sim1.set_resource_goal({'food':500})
    # sim1.simple_sim(num_villager)
    sim1.complex_sim(num_villager)

```

3\) You can change the detail level of output information in function ```summary_print```.
```python
def summary_print(self, cur_time):
    print("--------------------")
    print(self.resources) # the resource gathered so far
    print("The labor divison: ", end='')
    print(self.labor_division) # the current allocation plan
    print("Goal achieved in %d sec." % cur_time)

```

Currently, its output are like this:
```
--------------------
{'food': 5000, 'wood': 5525.0, 'gold': 5170, 'stone': 1920}
The labor divison: {'food': 14, 'wood': 11, 'gold': 8, 'stone': 3}
Goal achieved in 2193 sec.
--------------------
{'food': 5000, 'wood': 5182.5, 'gold': 4940, 'stone': 1840}
The labor divison: {'food': 15, 'wood': 11, 'gold': 8, 'stone': 3}
Goal achieved in 2125 sec.
```



## Hypotheses

This program modeled a simple version of *AoE II* with following hypothesis:

1. Villager spend no time in moving to or transporting resource to resource center (Town center, mill, lumber camp, mining camp etc.).

2. Town center continuously train villager until met the required villager number. (Because a viallager produced early can gather more resource than a late one).

3. Villager can be assigned to gather only one type of resource, and this assignment cannot be changed in future.

4. Villager will be automatically assigned to the "most-needed" resource after a villager is trained or finished buiding a house.

5. Only one town center is considered.

6. Farm does not exhaust, but for every 10 food received, 2.5 unit of wood is automatically deducted from current resource. 

## Acknowledgments

Big thanks to [Mr.Weible](https://ischool.illinois.edu/people/john-weible) for his fun, enlightening course as well as the great freedom he gave us in exploring topics we are really interested!




## Reference

1. The data of villagers gathering resources, and training time, I referred to data from [Age of Empires 2 Fandom](https://ageofempires.fandom.com/wiki/Villager_\(Age_of_Empires_II\)).

2. The idea of using a heap (priority queue) to accommodate and execute all the events one by one, is inspired by [Prof. Tim Roughgarden](http://timroughgarden.org/)'s [Algorithm Course](https://www.coursera.org/learn/algorithms-divide-conquer).




