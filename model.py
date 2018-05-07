
import fuzzy_logic as fl
from planners import Planner

from random import randint


class Behavior:

    id = None
    name = None
    tasks = []

    status = None           # available / inprogress / completed

    logger = None

    def __init__(self, behavior_specs, actions_names, logger):

        tasks = []
        for task_specs in behavior_specs['tasks_specs']:
            actions = []
            for action_id in task_specs['action_list']:
                action_name = actions_names[action_id]
                action_constraints = task_specs['constraints'].get(action_id, [])
                actions.append(Action(action_id, action_name, action_constraints, logger))
            tasks.append(Task(task_specs['id'], task_specs['name'], actions, logger))

        self.id = behavior_specs['id']
        self.name = behavior_specs['name']
        self.tasks = tasks
        self.status = 'available'
        self.logger = logger

    def update(self):

        # check if tasks completed / constraints removed
        for task in self.tasks:
            task.update(self)

        # check if behavior completed
        if all([True if task.status == 'completed' else False for task in self.tasks]):
            # behavior completed
            self.status = 'completed'
            self.logger.behavior_completed(self.id)

    def __getitem__(self, key):
        return self.get_task_by_id(key)

    def get_task_by_id(self, task_id):
        """
        Get task by id
        Returns Task / None
        """
        for task in self.tasks:
            if task.id == task_id:
                return task
        else:
            return None

    def get_tasks_ids(self, status_filter=None):
        """
        Get tasks by status
        Returns list of tasks' ids
        """
        tasks_list = []
        for task in self.tasks:
            if task.status == status_filter or status_filter is None:
                tasks_list.append(task.id)
        return tasks_list


class Task:

    id = None
    name = None
    actions = []

    status = None           # available / inprogress / completed
    assigned_to = None      # Agent / None

    logger = None

    def __init__(self, task_id, task_name, task_actions, logger):
        self.id = task_id
        self.name = task_name
        self.actions = task_actions
        self.status = 'available'
        self.logger = logger

    def assignment(self, agent):
        """
        called when an agent is assigned to this task
        """
        if self.status == 'available':
            self.status = 'inprogress'
            for action in self.actions:
                action.status = 'inqueue'
            self.assigned_to = agent
        else:
            raise ValueError('Cannot assign task %i with status `%s`' % (self.id, self.status))

    def update(self, behavior):

        # check if task is completed
        if self.status != 'completed':
            if all([True if action.status == 'completed' else False for action in self.actions]):
                # all actions of task completed - task completed
                self.status = 'completed'
                self.logger.task_completed(self.id)

        # update actions - check if constraints removed
        if self.status != 'completed':
            for action in self.actions:
                action.update(behavior)

    def __getitem__(self, key):
        return self.get_action_by_id(key)

    def get_action_by_id(self, action_id):
        """
        Get action by id
        Returns Action / None
        """
        for action in self.actions:
            if action.id == action_id:
                return action
        else:
            return None

    def get_actions_ids(self):  # , status_filter=None):
        """
        Get actions by status
        Returns list of actions' ids
        """
        actions_list = []
        for action in self.actions:
            actions_list.append(action.id)
        return actions_list

    def get_prev_action_of(self, action_id=None):
        """
        returns Action (previous of action_id, last one if action_id is None)
        returns None if action is the first action
        raises error if action wan not in task
        """
        last_action = None
        for action in self.actions:
            if action.id == action_id:
                return last_action
            else:
                last_action = action
        if action_id is None:
            return last_action
        else:
            # action given does not exist in task's actions
            raise ValueError('Action %s does not exist in Task %s' % (action_id, self.id))

    def get_next_action_of(self, action_id=None):
        """
        returns Action (next of action_id, first one if action_id is None)
        returns None if action given is the last action
        raises error if action wan not in task
        """
        action_found = True if action_id is None else False
        for action in self.actions:
            if action.id == action_id:
                # return next action
                action_found = True
            elif action_found:
                # return this action
                return action
        if action_found:
            # action given was the last action
            return None
        else:
            # action given does not exist in task's actions
            raise ValueError('Action %s does not exist in Task %s' % (action_id, self.id))


class Action:

    id = None
    name = None
    constraints = None

    status = None           # inqueue / inwaiting / inprogress / completed
    """
    inqueue does not care about constraints
    to see if there are active constraints check action.constraints
    when constraints are met, they are removed
    
    None            task not assigned (available)
    inqueue         task assigned (inprogress) - action not assigned
    inwaiting       task assigned (inprogress) - action assigned but not started (action setup not yet / agent waiting)
    inprogress      task assigned (inprogress) - action assigned and started (action setup ok / agent working)
    completed       task assigned (inprogress or completed) - action completed (no agent assigned)
    """
    assigned_to = None      # Agent / None
    __act_time_left = None

    logger = None

    def __init__(self, action_id, action_name, action_constraints, logger):
        self.id = action_id
        self.name = action_name
        self.constraints = action_constraints
        self.logger = logger

    def assignment(self, agent):
        """
        called when an agent is assigned to this action
        """
        if self.status == 'inqueue':
            self.status = 'inwaiting'
            self.assigned_to = agent
        else:
            raise ValueError('Cannot assign action %i with status `%s`' % (self.id, self.status))

    def setup(self, fuzzy_time):
        """
        called when an agent starts working on this action
        """
        if self.status == 'inwaiting' and not self.constraints:
            self.status = 'inprogress'
            # get rv from trapezoidal distribution (issue with cereal scenario)
            # self.__act_time_left = fuzzy_time.get_random_value()
            # get rv from uniform distribution
            self.__act_time_left = randint(fuzzy_time.value[1], fuzzy_time.value[2])
        else:
            raise ValueError('Cannot start action %i with status `%s`' % (self.id, self.status))

    def progress(self, timestep):
        """
        Returns if action has been completed
        """
        if self.status == 'inprogress':
            self.__act_time_left -= timestep
            if self.__act_time_left <= 0:
                # action completed
                self.status = 'completed'
                self.assigned_to = None
                self.__act_time_left = None
                self.logger.action_completed(self.id)
                return True
            else:
                return False
        else:
            raise ValueError('Cannot progress action %i with status `%s`' % (self.id, self.status))

    def update(self, behavior):

        # check if any constraints are met and remove them
        if self.constraints:
            to_remove = []
            for constraint in self.constraints:
                constraining_task_id, constraining_action_id = map(int, constraint.split('-'))
                if behavior[constraining_task_id][constraining_action_id].status == 'completed':
                    # constraint met - mark it to be removed
                    to_remove.append(constraint)

            # remove obsolete constraints
            for item in to_remove:
                self.constraints.remove(item)


class Team:

    id = None
    name = None
    agents = []

    status = None           # rest / work
    current_behavior = None

    planner = None

    logger = None
    reporter = None

    def __init__(self, team_specs, planner_type, logger, reporter):

        agents = []
        for agent_specs in team_specs['agents_specs']:
            agents.append(Agent(agent_specs['id'], agent_specs['name'], agent_specs['skills'], logger, reporter))

        self.id = team_specs['id']
        self.name = team_specs['name']
        self.agents = agents
        self.status = 'rest'
        self.logger = logger
        self.reporter = reporter
        self.planner = Planner(planner_type, self)

    def assign_behavior(self, behavior):

        self.current_behavior = behavior
        self.status = 'work'
        if self.current_behavior.status == 'available':
            self.current_behavior.status = 'inprogress'
        else:
            raise ValueError('Cannot assign behavior %i with status `%s`'
                             % (self.current_behavior.id, self.current_behavior.status))

    def assign_tasks_to_agents(self):

        if self.get_agents(status_filter='rest') and self.current_behavior.get_tasks_ids(status_filter='available'):

            # ask for assignments from planner
            assignments = self.planner()

            # assign tasks
            for agent_id, task_id in assignments.items():
                if task_id:
                    # assign task to agent
                    self[agent_id].assign_task(self.current_behavior[task_id])

    def progress(self, timestep):

        # assign tasks to resting agents
        self.assign_tasks_to_agents()

        # make progress
        for agent in self.agents:
            agent.progress(timestep)

        # update behavior / tasks / actions statuses
        self.current_behavior.update()

        # check if behavior completed [functional but not needed]
        # if self.current_behavior.status == 'completed':
        #     self.current_behavior = None
        #     self.status = 'rest'

        # # check if all agents are waiting at still constrained tasks
        # # NOTE: functional code but not necessary since time limit exists
        # elif (all([True if agent.status == 'wait' and agent.current_action.status == 'constrained'
        #            else False for agent in self.agents])):
        #     # progress blocked - behavior failed
        #     self.current_behavior.status = 'failed'
        #     self.current_behavior = None
        #     self.status = 'rest'

    def __getitem__(self, key):
        return self.get_agent_by_id(key)

    def get_agent_by_id(self, agent_id):
        """
        Get agent by id
        Returns Agent / None
        """
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        else:
            return None

    def get_agents(self, status_filter=None):
        """
        Get agents by status
        Returns list of Agents
        """
        agents_list = []
        for agent in self.agents:
            if agent.status == status_filter or status_filter is None:
                agents_list.append(agent)
        return agents_list


class Agent:

    id = None
    name = None
    skills = None                   # fuzzy time (t), robustness (r), error (e) for every action

    status = None                   # rest / wait / work
    current_task = None             # Task
    current_action = None           # Action
    exp_time_left_action = None     # Fuzzy or None (None when agent waiting or no current task/action assignment)

    logger = None
    reporter = None

    def __init__(self, agent_id, agent_name, agent_skills, logger, reporter):
        self.id = agent_id
        self.name = agent_name

        # add robustness/error level where needed in agent's skills
        # robustness = 10 - error
        for action_id, skill_stats in agent_skills.items():
            if not(set(skill_stats.keys()) == {'t', 'r'} or set(skill_stats.keys()) == {'t', 'e'}):
                raise ValueError('Unexpected skill_stats `%s`' % skill_stats.keys())
            if 'r' in skill_stats.keys():
                agent_skills[action_id]['e'] = 10 - agent_skills[action_id]['r']
            elif 'e' in skill_stats.keys():
                agent_skills[action_id]['r'] = 10 - agent_skills[action_id]['e']

        # convert time intervals to fuzzy times
        for action_id in agent_skills.keys():
            agent_skills[action_id]['t'] = fl.Fuzzy(agent_skills[action_id]['t'])

        self.skills = agent_skills
        self.status = 'rest'
        self.logger = logger
        self.reporter = reporter

    def assign_task(self, task):
        """
        Called by planner to assign new task to agent
        """
        # task assignment
        self.current_task = task
        self.current_task.assignment(self)
        self.logger.agent_assigned_task(self.id, self.current_task.id)
        # action assignment
        self.self_assign_action()

    def self_assign_action(self):
        """
        Called by agent to self-assign the next action of current task
        """
        prev_action_id = self.current_action.id if self.current_action is not None else None
        next_action = self.current_task.get_next_action_of(prev_action_id)
        if next_action is not None:
            # assign next action
            self.current_action = next_action
            self.current_action.assignment(self)
            self.logger.agent_assigned_action(self.id, self.current_task.id, self.current_action.id,
                                              self.current_action.status)
            self.reporter.report_action_robustness(self.current_task.id, self.current_action.id,
                                                   self.skills[self.current_action.id]['r'])

            if self.current_action.constraints:
                # start waiting
                self.status = 'wait'
                self.exp_time_left_action = None

            else:
                # start working
                self.status = 'work'
                self.exp_time_left_action = self.skills[self.current_action.id]['t']
                self.current_action.setup(self.skills[self.current_action.id]['t'])
                self.logger.agent_started_working(self.id, self.current_task.id, self.current_action.id)

        else:
            # if no next action exists, put agent to rest
            self.status = 'rest'
            self.current_task = None
            self.current_action = None
            self.exp_time_left_action = None
            self.logger.agent_at_rest(self.id)

    def progress(self, timestep):

        # if waiting, check if no need to wait any longer
        if self.status == 'wait' and not self.current_action.constraints:
            # start working
            self.status = 'work'
            self.exp_time_left_action = self.skills[self.current_action.id]['t']
            self.current_action.setup(self.skills[self.current_action.id]['t'])
            self.logger.agent_started_working(self.id, self.current_task.id, self.current_action.id)

        # if working, progress current action
        if self.status == 'work':
            # report agent working
            self.reporter.report_agent_status(self.id, self.status)
            # make progress on current action
            action_completed = self.current_action.progress(timestep)
            # check if action completed
            if action_completed:
                # self-assign to next action of task / put at rest if no next action exists
                self.self_assign_action()
            else:
                # roll left timestep from exp_time_left_action
                # (same as subtract but fuzzy points cannot go below 0)
                self.exp_time_left_action = self.exp_time_left_action.roll_left(timestep)

        elif self.status in ['rest', 'wait']:
            # report agent resting/waiting/
            self.reporter.report_agent_status(self.id, self.status)
            pass

        else:
            raise ValueError('Why you %s-ing?' % self.status)

    def calc_actions_tt(self, actions_list):
        """
        get total time needed for agent to complete all actions of given list
        returns fuzzy
        """
        tt = fl.Fuzzy((0, 0))
        for action_id in actions_list:
            tt += self.skills[action_id]['t']
        return tt

    def calc_actions_mr(self, actions_list):
        """
        get minimum robustness expected from agent to complete all actions of given list
        returns crisp
        """
        mr = 10
        for action_id in actions_list:
            if mr > self.skills[action_id]['r']:
                mr = self.skills[action_id]['r']
        return mr

    def calc_actions_me(self, actions_list):
        """
        get maximum error expected from agent to complete all actions of given list
        returns crisp
        """
        me = 0
        for action_id in actions_list:
            if me < self.skills[action_id]['e']:
                me = self.skills[action_id]['e']
        return me
