## Overview

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

| | |
| --- | --- |
| Behavior | assigned to a team with the goal of completing it |
| Tasks | entities of the behavior that are separately assigned to agents and can be progressed in parallel |
| Actions | entities of any task, motion sequences driven by a single basic goal |
| Team | group of agents that work on the same behavior |
| Agents | entities of the team, can have different skill sets |


### Visualization

![Daisy flower](https://ars.els-cdn.com/content/image/1-s2.0-S1389041716300596-gr2.jpg)

Behavior visualized as a daisy flower.
Tasks are represented as petals, actions as edges and events as vertices.
Constraints between actions are denoted with red edges connecting events on different petals.

![Daisy petals](https://ars.els-cdn.com/content/image/1-s2.0-S1389041716300596-gr3.jpg)

Detailed visualization of actions, events and constraints on a daisy behavior.



## Algorithms

### Basic Planner

Created for comparative evaluation of the other planners.
Prefers to assign unconstrained tasks than constrained ones to agents, chooses randomly between available options.


### Basic Plus Planner

Created for comparative evaluation of the other planners.
Prefers to assign tasks with less constraints than ones with more to agents, chooses randomly between available options.


### Daisy Planner v1

Detailed description of the algorithm can be found in the paper "Time-informed task planning in multi-agent collaboration" [1]

In this version, the planner estimates the assignment cost of each available task for a given agent and assigns to the agent the task with the minimum cost.

Assignment cost (`AC`) for a given task and a given agent is computed according to the formula:
```
AC = TT / (1 + MR)
```
where:
- `TT` is the total time needed for the execution of a given task by a given agent
- `MR` is the minimum level of robustness expected of a given agent across all actions of a given task

In the case that no task is fully available due to action constraints, the agent is assigned the task restricted by the least number of constraints.


### Daisy Planner v2

Detailed description of the algorithm can be found in the paper "Collaboration of heterogeneous agents in time constrained tasks" [2]

In this version, the planner estimates the team benefit of assigning each available task to a given agent and assigns to the agent the task with the maximum score.

Team benefit (`TB`) for a given task and a given agent is computed according to the formula:
```
TB = max{AC<sub>i</sub> - AC<sub>x</sub>}
```
where:
- `AC` is the assignment cost
- `x` is the agent for whom team benefit is calculated
- `i` is every other agent

Assignment cost (`AC`) for a given task and a given agent is computed according to the formula:
```
AC = TT * ME
```
where:
- `TT` is the total time needed for the execution of a given task by a given agent
- `ME` is the maximum level of error expected of a given agent across all actions of a given task

In the case that no task is fully available due to action constraints, the agent is assigned the task restricted by the least number of constraints.


### New Planner

Detailed description of the proposed algorithm can be found [here](/NEW_PLANNER.md)

In order to assign tasks to available agents, this planner calculates the relative value for each possible assignment, and chooses the ones that produce the maximum sum of relative values.

Relative value (`RV`) of an assignment for a given task and a given agent is computed according to the formula:
```
RV = AV / MVS
```
where:
- `AV` is the absolute value of a specific assignment
- `MVS` is the maximum vanilla score of the task under consideration

Absolute value (`AV`) of an assignment for a given task and a given agent is computed according to the formula:
```
AV = MR<sup>m</sup> / TT<sup>(1-m)</sup>
```
where:
- `MR` is the minimum level of robustness expected of a given agent across all actions of a given task
- `TT` is the total time needed for the an agent to complete a task, considering the time expected for the agent to be available and the time expected for the task to be free of constraints
- `m` is the planners hyperparameter which takes values in the `[0,1]` and shows if the assignments should be made based only on robustness (`0`), or only on total time (`1`), or on any weighted combination of the two (e.g. `0.5`)

Maximum vanilla score (`MVS`) for a given task is the maximum value of vanilla scores (`VS`) a task can have by being assigned to different agents of the team.

Vanilla score (`VS`) for a given task and a given agent is computed according to the formula:
```
VS = MR<sup>m</sup> / TT<sub>v</sub><sup>(1-m)</sup>
```
where:
- `TT<sub>v</sub>` is the vanilla total time needed for an agent to complete a task, assuming the agent is readily available and all actions of the task are unconstrained


### Scenario Generator

A scenario generator is implemented for testing the effectiveness of the planning algorithms on an unlimited number of different scenarios, in addition to the baseline scenarios of 'salad preparation' ([1]) and 'cereal preparation' ([2]).

The number of agents in the team, and the number of tasks the behavior consists of are all customizable.
The probabilities of constrains existing between actions of different tasks can also be customized.



## Experimental Design

### Simulations and Reports

The code provided gives the ability to test any subset of the aforementioned planning algorithms, on any number of different scenarios, for any number of times each.
Apart from the randomly generated scenarios with customizable numbers of agents and tasks, the fixed scenarios of salad and cereal preparation (as described in [1] and [2] respectively) can also be used. 

The simulation logger (if enabled) can provide a log of all the states and events that occurred during the simulation,
and the simulation reporter (if enabled) can provide statistics for the completed simulation as well as save these results as a row in the appropriate csv file.

The data kept by the reporter after each simulation consists of 
the behavior status, 
the total time spent by the team on the behavior, 
the maximum time it would take for the behavior to be completed by the team,
the mean robustness level achieved across all tasks,
the time of concurrent activity amongst all agents,
and the time each agent was resting, waiting and working through out the simulation. 


### Evaluation Metrics

The statistics provided for assessing each algorithms efficiency, after a sufficient number of simulations for each one have been run, are the following:

- number of times the behavior was successfully completed
- mean of distribution of total time spent for each behavior by the team
- mean of distribution of robustness level achieved for each behavior by the team
- sum of times every agent of the team spent resting, waiting, and working



## Project Guide

### Code structure

| File | Description |
| --- | --- |
| [model.py](/model.py) | Contains all the basic classes needed for the experiment, namely Behavior, Task, Action, Team & Agent. |
| [fuzzy_logic.py](/fuzzy_logic.py) | Contains class Fuzzy, used for the modeling & handling of time intervals as fuzzy numbers. |
| [planners.py](/planners.py) | Contains class Planner, which contains all the planning algorithms described above. |
| [helpers.py](/helpers.py) | Contains helper functions for the planning algorithms. |
| [scenario.py](/scenario.py) | Contain class Scenario, which can produce custom scenarios of any number of tasks and agents, as well as the 'salad' and 'cereal' scenarios. |
| [simulation.py](/simulation.py) | Contains class Simulation, used for running a single trial given a scenario and a planner algorithm. |
| [experiment.py](/experiment.py) | Contains class Experiment, used for running simulations multiple times on different scenarios and planners. |
| [sim_logger.py](/sim_logger.py) | Contains class Logger, used for live logging of the simulation. |
| [sim_reporter.py](/sim_reporter.py) | Contains class Reporter, used for storing results from simulations / experiments in csv files. |


### Code dependencies

- Python 3.6
- scipy 1.0.1
- colorama 0.3.9


### Running the code

- To run a **single simulation**, set the desired simulation parameters at the end of the simulation.py file, and run it with the command `python simulation.py` while inside the project directory.
By setting `logger_verbose_level` to `basic` in the simulation parameters, the whole history of states and actions of the simulation will be printed.

- To run a **full experiment**, set the desired experiment parameters at the end of the experiment.py file, and run it with the command `python experiment.py` while inside the project directory.
By default the reporter will produce a csv file containing the experiment results and save it in the `/reports` folder inside the project directory.



## References

[1]: [Time-informed task planning in multi-agent collaboration](https://www.sciencedirect.com/science/article/pii/S1389041716300596)  
[2]: [Collaboration of heterogeneous agents in time constrained tasks](http://ieeexplore.ieee.org/document/7803314/)
