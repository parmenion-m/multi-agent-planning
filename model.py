
import random


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

    logger = None

    def __init__(self, task_id, task_name, task_actions, logger):
        self.id = task_id
        self.name = task_name
        self.actions = task_actions
        self.status = 'available'
        self.logger = logger

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

    def get_next_action(self, prev_action_id=None):
        """
        Get the first action of the task if prev_action is None,
        or the next action otherwise,
        or None if prev_action was the last action
        Returns Action / None
        """
        prev_action_found = True if prev_action_id is None else False
        for action in self.actions:
            if action.id == prev_action_id:
                # return next action
                prev_action_found = True
            elif prev_action_found:
                # return this action
                return action
        if prev_action_found:
            # prev_action was the last action
            return None
        else:
            # prev_action does not exist in task's actions
            raise ValueError('Invalid prev_action_id %s for task %s' % (prev_action_id, self.id))


class Action:

    id = None
    name = None
    constraints = None

    status = None           # available / constrained / inprogress / completed
    __act_time_left = None

    logger = None

    def __init__(self, action_id, action_name, action_constraints, logger):
        self.id = action_id
        self.name = action_name
        self.constraints = action_constraints
        self.status = 'constrained' if self.constraints else 'available'
        self.logger = logger

    def setup(self, time_interval):
        if self.status == 'available':
            self.status = 'inprogress'
            self.__act_time_left = random.randint(time_interval[0], time_interval[1])
        else:
            raise ValueError('Cannot assign action %i with status `%s`' % (self.id, self.status))

    def progress(self, timestep):
        """
        Returns if action has been completed
        """
        if self.status == 'inprogress':
            self.__act_time_left -= timestep
            if self.__act_time_left <= 0:
                # action completed
                self.status = 'completed'
                self.__act_time_left = None
                self.logger.action_completed(self.id)
                return True
            else:
                return False
        else:
            raise ValueError('Cannot progress action %i with status `%s`' % (self.id, self.status))

    def update(self, behavior):

        # check if any constraints are met and remove them
        if self.status == 'constrained':
            to_remove = []
            for constraint in self.constraints:
                constraining_task_id, constraining_action_id = map(int, constraint.split('-'))
                if behavior[constraining_task_id][constraining_action_id].status == 'completed':
                    # constraint met - mark it to be removed
                    to_remove.append(constraint)

            # remove obsolete constraints
            for item in to_remove:
                self.constraints.remove(item)

            # make action available if not constraint left
            if not self.constraints:
                self.status = 'available'
                self.logger.action_available(self.id)


class Team:

    id = None
    name = None
    agents = []

    status = None           # rest / work
    current_behavior = None

    planner = None

    logger = None
    reporter = None

    def __init__(self, team_specs, planner, logger, reporter):

        agents = []
        for agent_specs in team_specs['agents_specs']:
            agents.append(Agent(agent_specs['id'], agent_specs['name'], agent_specs['skills'], logger, reporter))

        self.id = team_specs['id']
        self.name = team_specs['name']
        self.agents = agents
        self.status = 'rest'
        self.planner = planner
        self.logger = logger
        self.reporter = reporter

    def assign_behavior(self, behavior):

        self.current_behavior = behavior
        self.status = 'work'
        if self.current_behavior.status == 'available':
            self.current_behavior.status = 'inprogress'
        else:
            raise ValueError('Cannot assign behavior %i with status `%s`'
                             % (self.current_behavior.id, self.current_behavior.status))

    def assign_tasks_to_agents(self):

        if self.get_agents(status_filter='rest'):

            # ask for assignments from planner
            assignments = self.planner(self)

            # assign tasks
            for agent_id, task_id in assignments.items():
                if task_id:
                    # assign task to agent
                    self[agent_id].assign_task(self.current_behavior[task_id])
                else:
                    self[agent_id].status = 'sleep'

    def progress(self, timestep):

        # assign tasks to resting agents
        self.assign_tasks_to_agents()

        # make progress
        for agent in self.agents:
            agent.progress(timestep)

        # update behavior / tasks / actions statuses
        self.current_behavior.update()

        # check if behavior completed
        if self.current_behavior.status == 'completed':
            self.current_behavior = None
            self.status = 'rest'

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
    skills = None                   # time intervals & robustness levels for every action of every task

    status = None                   # rest / wait / work / sleep
    current_task = None             # Task
    current_action = None           # Action

    logger = None
    reporter = None

    def __init__(self, agent_id, agent_name, agent_skills, logger, reporter):
        self.id = agent_id
        self.name = agent_name
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
        self.logger.agent_assigned_task(self.id, self.current_task.id)
        if self.current_task.status == 'available':
            self.current_task.status = 'inprogress'
        else:
            raise ValueError('Cannot assign task %i with status `%s`'
                             % (self.current_task.id, self.current_task.status))
        # action assignment
        self.self_assign_action()

    def self_assign_action(self):
        """
        Called by agent to self-assign the next action of current task
        """
        prev_action_id = self.current_action.id if self.current_action is not None else None
        next_action = self.current_task.get_next_action(prev_action_id)
        if next_action is not None:
            # assign next action
            self.current_action = next_action
            self.logger.agent_assigned_action(self.id, self.current_task.id, self.current_action.id,
                                              self.current_action.status)
            self.reporter.report_action_robustness(self.current_task.id, self.current_action.id,
                                                   self.skills[self.current_action.id]['r'])

            if self.current_action.status == 'available':
                # start working
                self.current_action.setup(self.skills[self.current_action.id]['t'])
                self.status = 'work'
                self.logger.agent_started_working(self.id, self.current_task.id, self.current_action.id)
            elif self.current_action.status == 'constrained':
                # start waiting
                self.status = 'wait'
            else:
                raise ValueError('Cannot assign action %i with status `%s`'
                                 % (self.current_action.id, self.current_action.status))
        else:
            # if no next action exists, put agent to rest
            self.status = 'rest'
            self.current_task = None
            self.current_action = None
            self.logger.agent_at_rest(self.id)

    def progress(self, timestep):

        # if waiting, check if no need to wait any longer
        if self.status == 'wait' and self.current_action.status == 'available':
            self.current_action.setup(self.skills[self.current_action.id]['t'])
            self.status = 'work'
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

        elif self.status in ['wait', 'sleep']:
            # report agent waiting/sleeping
            self.reporter.report_agent_status(self.id, self.status)
            pass

        else:
            raise ValueError('Why you %s-ing?' % self.status)

    # def calc_task_tt(self, task_id):
    #     """
    #     get total time needed for agent to complete all steps of given task
    #     returns fuzzy
    #     """
    #     tt = fl.Fuzzy((0, 0))
    #     for action_skills in self.skills[task_id].values():
    #         interval = action_skills['t']
    #         tt += fl.Fuzzy(interval)
    #     return tt
    #
    # def calc_task_mr(self, task_id):
    #     """
    #     get minimum robustness level for agent across all steps of given task
    #     returns crisp
    #     """
    #     mr = 10
    #     for action_skills in self.skills[task_id].values():
    #         robustness = action_skills['r']
    #         if mr > robustness:
    #             mr = robustness
    #     return mr
    #
    # def calc_task_ac(self, task_id):
    #     """
    #     get assignment cost for assigning given task to agent
    #     returns crisp
    #     """
    #     tt = fl.Fuzzy((0, 0))
    #     mr = 10
    #     for action_skills in self.skills[task_id].values():
    #         interval = action_skills['t']
    #         tt += fl.Fuzzy(interval)
    #         robustness = action_skills['r']
    #         if mr > robustness:
    #             mr = robustness
    #     ac = tt.defuzzify() / (1 + mr)
    #     return ac
    #
    # def get_action_t(self, task_id, action_id):
    #     return fl.Fuzzy(self.skills[task_id][action_id]['t'])
    #
    # def get_action_r(self, task_id, action_id):
    #     return self.skills[task_id][action_id]['r']
