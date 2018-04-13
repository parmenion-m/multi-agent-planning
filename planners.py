"""
All planners take as input the current instance of the working behavior
and return a dictionary of assignments in the form {agent_id : task_id}
"""

import fuzzy_logic as fl


def daisy_planner_v1(team):

    assignments = {}

    # --- get available tasks ids with their number of constraints ---
    tasks_available = {}
    for task in team.current_behavior.tasks:
        if task.status == 'available':
            """
            many different steps of a task can have many different constraints
            """
            constraints_num = 0
            for action in task.actions:
                # print(action.constraints)
                constraints_num += len(action.constraints)
            tasks_available[task.id] = constraints_num

    # --- for each resting agent ---
    for resting_agent in team.get_agents(status_filter='rest'):

        # --- get list of tasks ids with the least number of constraints ---
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

            # --- calculate assignment costs for tasks under consideration ---
            ac_scores = {}
            for task_id in tasks_considered:

                # initialize total time & min robustness
                tt = fl.Fuzzy((0, 0))
                mr = 10

                # for each action of task
                for action in team.current_behavior[task_id].actions:
                    # find time needed & robustness expected
                    t = resting_agent.skills[action.id]['t']
                    r = resting_agent.skills[action.id]['r']
                    # update total time & min robustness
                    tt += fl.Fuzzy(t)
                    if r < mr:
                        mr = r

                # calculate assignment cost
                ac_scores[task_id] = tt.defuzzify() / (1 + mr)

            task_selected = min(ac_scores, key=ac_scores.get)

        # create assignment
        assignments[resting_agent.id] = task_selected
        # remove task from list of available tasks
        if task_selected:
            del tasks_available[task_selected]

    return assignments
