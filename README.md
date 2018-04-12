### Overview

The purpose of this project is to simulate a multi-agent collaboration scenario and test the effect on teamwork
 efficiency that different planning algorithms have.

More specifically this work tries to compare the effectiveness of different published and proposed
 versions of the DaisyPlanner algorithm, presented by the work of ICS-FORTH researchers
 Michail Maniadakis, Panos Trahanias, et.al. on multi-agent collaboration task planning.

DaisyPlanner is a planning algorithm used for assigning tasks to a group of heterogeneous agents according to their skills.
 It employs Immediate Optimal Planning and Multi-Criteria Evaluation in an effort to be a fast, flexible and effective
 solution to the planning problem.


### Immediate Optimal Planning

In unstructured environments, where unexpected events can often disrupt the execution of actions, it can be considered impractical
 to devote resources into the estimation of globally optimal plans that consist of long sequences of action assignments.
 Immediate Optimal Planning (IOP) refers to the progressive approaches on planning that develop optimal short-term plans based on the current state of the world.
 Short-term optimal plans are created by matching agents to tasks after considering the agents' statuses and skills.


### Multi-Criteria Evaluation

DaisyPlanner considers composite time-informed criteria that enable the ranking of alternative assignments of tasks to agents.
 Namely, these criteria are the time required for the execution of a task and the quality of performance each agent is expected to achieve.
 Of course the status of each agent and task is also considered during each planning phase.
 Fuzzy numbers are used for encoding the temporal information and crisp values of robustness levels are used for representing the quality of performance expected.
 Fuzzy arithmetic is used to develop the multi-criteria measures needed for the comparison of alternative planning scenarios.


### Fuzzy Logic

Time intervals are encoded as a trapezoidal fuzzy number represented by a quadruplet of the form (a, b, c, d).
 In this quadruplet, b is assigned the estimated lower bound of a time interval and c is assigned the upper one.
 To model the inherited  uncertainty of these estimations, a is assigned a value 10% less than b, and d a value of 10% more than c.
 So, as an example, the fuzzy time "approximately 4 to 6 min" would be represented by the trapezoid (3.6, 4, 6, 6.6).

Defuzzification is the process of mapping a fuzzy number to an ordinary crisp value.
 In this work this is accomplished by following the classic graded mean integration.
 Defuzzification is also used in this work as the means of comparing two fuzzy numbers.
 Multiple other operations between fuzzy and/or crisp numbers are supported in the fuzzy logic library provided with this project.


### Terminology

Behavior    assigned to a team with the goal of completing it
Tasks       entities of the behavior that are separately assigned to agents and can be progressed in parallel
Actions     entities of any task, motion sequences driven by a single basic goal

Team        a group of agents that work toward a common goal
Agent       an entity of the team, differentiated by its own skills


### Visualization

![Daisy flower](https://ars.els-cdn.com/content/image/1-s2.0-S1389041716300596-gr2.jpg)

Behavior visualized as a daisy flower.
 Tasks are represented as petals, actions as edges and events as vertices.
 Constraints between actions are denoted with red edges connecting events on different petals.

![Daisy petals](https://ars.els-cdn.com/content/image/1-s2.0-S1389041716300596-gr3.jpg)

Detailed visualization of actions, events and constraints on a daisy behavior.


### Algorithms

The algorithms implemented:

#### DaisyPlanner v1

[Time-informed task planning in multi-agent collaboration](https://www.sciencedirect.com/science/article/pii/S1389041716300596)

In this version, the planner estimates the cost of each available task for a given agent, and assigns to the agent the task
 with the minimum cost. Assignment cost (`AC`) is computed according to the formula:
```
AC = TT / (1 + MR)
```
where:
- `TT` is the total time needed for the execution of a given task by a given agent
- `MR` is the minimum level of robustness of a given agent across all actions of a given task

In the case that no task is fully available due to action constraints, the agent is assigned the task restricted by the
 least number of constraints.

#### DaisyPlanner v2

[Collaboration of heterogeneous agents in time constrained tasks](http://ieeexplore.ieee.org/document/7803314/)

To be added...

#### RandomPlanner

To be added...

#### Scenario Generator

A scenario generator is implemented for testing the effectiveness of the planning algorithms on an unlimited number of different scenarios, in addition to the baseline scenario of 'salad preparation'.
 The number of agents in the team, the number of tasks in the behavior and the number of different actions available in the scenario are all customizable.
 The probabilities of constrains existing between actions of different tasks can also be customized as well.


### Evaluation Metrics

To be added...


### Experimental Results

To be added...


#### Code dependencies

- Python 3.6
- colorama 0.3.9
- scipy 1.0.1


#### Code structure

To be added...


### Reproducing Results

To run a single simulation run simulation.py

More to be added...


### Credits

To be added...
