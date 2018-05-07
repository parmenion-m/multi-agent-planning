
from helpers import *

from random import shuffle


class Planner:

    team = None
    logger = None

    selected_planner = None

    m = None                        # new_planner hyperparameter
    max_vanilla_scores = None       # new_planner persistent data

    team_benefit_scores = None      # daisy_planner_v2 persistent data

    def __init__(self, planner_algorithm, team):

        self.team = team
        self.logger = team.logger
        self.m = None
        self.max_vanilla_scores = None
        self.team_benefit_scores = None

        # base / base+ / dpv1 / dpv2 / new-0.0 / new-0.5 / new-1.0
        if planner_algorithm == 'base':
            self.selected_planner = self.basic_planner
        elif planner_algorithm == 'base+':
            self.selected_planner = self.basic_plus_planner
        elif planner_algorithm == 'dpv1':
            self.selected_planner = self.daisy_planner_v1
        elif planner_algorithm == 'dpv2':
            self.selected_planner = self.daisy_planner_v2
        elif planner_algorithm.split('-')[0] == 'new':
            self.selected_planner = self.new_planner
            self.m = float(planner_algorithm.split('-')[1])
        else:
            raise ValueError('Unknown planner_algorithm: `%s`' % planner_algorithm)

    def __call__(self):

        return self.selected_planner()

    """
    All planners take as input the current state of the team (including the working behavior) from self.team
    and return a dictionary of assignments in the form of {agent_id : task_id}
    """

    def basic_planner(self):
        """
        prefers to assign unconstrained tasks than constrained ones to agents
        chooses randomly between available options
        """
        assignments = {}

        # get task ids from available tasks and split them into constrained and not constrained ones
        tasks_unconstrained = []
        tasks_constrained = []
        for task in self.team.current_behavior.tasks:
            if task.status == 'available':
                # check if any action of task is constrained
                # throw task id into the corresponding list
                for action in task.actions:
                    if action.constraints:
                        tasks_constrained.append(task.id)
                        break
                else:
                    tasks_unconstrained.append(task.id)

        shuffle(tasks_constrained)
        shuffle(tasks_unconstrained)

        # for each resting agent
        for resting_agent in self.team.get_agents(status_filter='rest'):
            # random task from not constrained tasks if any available
            if tasks_unconstrained:
                assignments[resting_agent.id] = tasks_unconstrained.pop()
            # random task from constrained tasks if any available
            elif tasks_constrained:
                assignments[resting_agent.id] = tasks_constrained.pop()
            # None if no task left to assign
            else:
                assignments[resting_agent.id] = None

        self.logger.planner_assignments(assignments)
        return assignments

    def basic_plus_planner(self):
        """
        prefers to assign tasks with less constraints than ones with more to agents
        chooses randomly between available options
        """
        assignments = {}

        # get available tasks ids with their number of constraints
        tasks_available = get_available_tasks_with_constraints_num(self.team.current_behavior)

        # for each resting agent
        for resting_agent in self.team.get_agents(status_filter='rest'):

            # get list of tasks ids with the least number of constraints
            tasks_considered = []
            min_constraints = 99999
            for task_id, constraints_num in tasks_available.items():
                if constraints_num < min_constraints:
                    min_constraints = constraints_num
                    tasks_considered = [task_id]
                elif constraints_num == min_constraints:
                    tasks_considered.append(task_id)

            if len(tasks_considered) == 0:
                task_selected = None
            elif len(tasks_considered) == 1:
                task_selected = tasks_considered[0]
            else:
                # choose randomly
                shuffle(tasks_considered)
                task_selected = tasks_considered[0]

            # create assignment
            assignments[resting_agent.id] = task_selected
            # remove task from list of available tasks
            if task_selected:
                del tasks_available[task_selected]

        self.logger.planner_assignments(assignments)
        return assignments

    def daisy_planner_v1(self):
        """
        prefers to assign tasks with less constraints than ones with more to agents
        chooses between available options based on assignment cost
        """
        assignments = {}

        # get available tasks ids with their number of constraints
        tasks_available = get_available_tasks_with_constraints_num(self.team.current_behavior)

        # for each resting agent
        for resting_agent in self.team.get_agents(status_filter='rest'):

            # get list of tasks ids with the least number of constraints
            tasks_considered = []
            min_constraints = 99999
            for task_id, constraints_num in tasks_available.items():
                if constraints_num < min_constraints:
                    min_constraints = constraints_num
                    tasks_considered = [task_id]
                elif constraints_num == min_constraints:
                    tasks_considered.append(task_id)

            if len(tasks_considered) == 0:
                task_selected = None
            elif len(tasks_considered) == 1:
                task_selected = tasks_considered[0]
            else:
                # calculate assignment costs for tasks under consideration
                ac_scores = {}
                for task_id in tasks_considered:
                    actions_list = self.team.current_behavior[task_id].get_actions_ids()
                    # get total time
                    tt = resting_agent.calc_actions_tt(actions_list)
                    # get minimum robustness
                    mr = resting_agent.calc_actions_mr(actions_list)
                    # calculate assignment cost
                    ac_scores[task_id] = tt.defuzzify() / (1 + mr)
                # select task with minimum assignment cost
                task_selected = min(ac_scores, key=ac_scores.get)

            # create assignment
            assignments[resting_agent.id] = task_selected
            # remove task from list of available tasks
            if task_selected:
                del tasks_available[task_selected]

        self.logger.planner_assignments(assignments)
        return assignments

    def daisy_planner_v2(self):
        """
        prefers to assign tasks with less constraints than ones with more to agents
        chooses between available options based on team benefit
        """

        # calc team_benefit_scores the first time the planner runs
        if self.team_benefit_scores is None:

            # tasks' ids & agents
            tasks_ids = self.team.current_behavior.get_tasks_ids()
            agents_all = self.team.get_agents()

            # assignment costs
            ac = {agent.id: {task_id: None for task_id in tasks_ids} for agent in agents_all}

            for agent in agents_all:
                for task_id in tasks_ids:
                    total_time = agent.calc_actions_tt(self.team.current_behavior[task_id].get_actions_ids())
                    max_error = agent.calc_actions_me(self.team.current_behavior[task_id].get_actions_ids())
                    ac[agent.id][task_id] = total_time * max_error

            # team benefit scores
            tb = {agent.id: {task_id: None for task_id in tasks_ids} for agent in agents_all}

            for task_id in tasks_ids:
                for agent in agents_all:
                    ac_diffs = []
                    for other_agent in agents_all:
                        if agent.id != other_agent.id:
                            fuzzy_diff = ac[other_agent.id][task_id] - ac[agent.id][task_id]
                            ac_diffs.append(fuzzy_diff.defuzzify())
                    tb[agent.id][task_id] = max(ac_diffs) if ac_diffs else 1

            # save the team benefit scores for later reference
            self.team_benefit_scores = tb
            self.logger.planner_dpv2_benefit_table(self.team_benefit_scores)

        assignments = {}

        # get available tasks ids with their number of constraints
        tasks_available = get_available_tasks_with_constraints_num(self.team.current_behavior)

        # for each resting agent
        for resting_agent in self.team.get_agents(status_filter='rest'):

            # get list of tasks ids with the least number of constraints
            tasks_considered = []
            min_constraints = 99999
            for task_id, constraints_num in tasks_available.items():
                if constraints_num < min_constraints:
                    min_constraints = constraints_num
                    tasks_considered = [task_id]
                elif constraints_num == min_constraints:
                    tasks_considered.append(task_id)

            if len(tasks_considered) == 0:
                task_selected = None
            elif len(tasks_considered) == 1:
                task_selected = tasks_considered[0]
            else:
                # select task with maximum team benefit score
                tasks_considered_benefit = {}
                for task_id in tasks_considered:
                    tasks_considered_benefit[task_id] = self.team_benefit_scores[resting_agent.id][task_id]
                task_selected = max(tasks_considered_benefit, key=tasks_considered_benefit.get)

            # create assignment
            assignments[resting_agent.id] = task_selected
            # remove task from list of available tasks
            if task_selected:
                del tasks_available[task_selected]

        self.logger.planner_assignments(assignments)
        return assignments

    def new_planner(self):

        # calc max_vanilla_scores the first time the planner runs
        if self.max_vanilla_scores is None:
            """
            vanilla scores do not consider:
            - constraints between tasks
            - expected times for agent to be available for assignment
            they exist so that a theoretical maximum value score for each task can be calculated
            in order to normalize the actual scores later
            """

            # calc vanilla scores for each task theoretically assigned to each agent
            vanilla_scores = {agent.id: {task.id: None for task in self.team.current_behavior.tasks}
                              for agent in self.team.agents}
            for agent in self.team.agents:
                for task in self.team.current_behavior.tasks:
                    actions_list = self.team.current_behavior[task.id].get_actions_ids()

                    tt = self.team[agent.id].calc_actions_tt(actions_list)
                    mr = self.team[agent.id].calc_actions_mr(actions_list)
                    vs = mr ** self.m / tt.defuzzify() ** (1-self.m)
                    vanilla_scores[agent.id][task.id] = vs

            # get the maximum vanilla score each task can achieved if assigned to the most appropriate agent
            max_vanilla_scores = {}
            for task in self.team.current_behavior.tasks:
                max_score = 0
                for agent in self.team.agents:
                    if vanilla_scores[agent.id][task.id] > max_score:
                        max_score = vanilla_scores[agent.id][task.id]
                max_vanilla_scores[task.id] = max_score

            # save the max vanilla scores for later reference
            self.max_vanilla_scores = max_vanilla_scores
            self.logger.planner_new_vanilla_table(self.max_vanilla_scores)

        # init values table
        values = {agent.id: {task_id: None
                             for task_id in self.team.current_behavior.get_tasks_ids(status_filter='available')}
                  for agent in self.team.agents}

        # calculate values for each possible assignment of task to agent
        for agent in self.team.agents:
            for task_id in self.team.current_behavior.get_tasks_ids(status_filter='available'):
                # get expected time to complete task
                tt = calc_exp_time_to_complete_next_task(self.team, agent, self.team.current_behavior[task_id])
                # get expected robustness level
                mr = agent.calc_actions_mr(self.team.current_behavior[task_id].get_actions_ids())
                # calculate absolute value of assignment
                av = mr ** self.m / tt.defuzzify() ** (1-self.m) if tt else None
                # calculate value of assignment relative to max vanilla scores
                rv = av / self.max_vanilla_scores[task_id] if av else -1
                values[agent.id][task_id] = rv

        self.logger.planner_new_values_table(values)

        assignments = {}
        for resting_agent in self.team.get_agents(status_filter='rest'):
            if values[resting_agent.id]:
                task_selected = max(values[resting_agent.id], key=values[resting_agent.id].get)
                assignments[resting_agent.id] = task_selected
                for agent in self.team.agents:
                    del values[agent.id][task_selected]
            else:
                # more agents resting than tasks available (agents finished prev task simultaneously)
                assignments[resting_agent.id] = None

        self.logger.planner_assignments(assignments)
        return assignments
