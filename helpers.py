
import fuzzy_logic as fl


def get_available_tasks_with_constraints_num(behavior):
    """
    returns {task_id : constraints_num}
    """
    tasks_available = {}
    for task in behavior.tasks:
        if task.status == 'available':
            """
            many different actions of a task can have many different constraints
            """
            constraints_num = 0
            for action in task.actions:
                constraints_num += len(action.constraints)
            tasks_available[task.id] = constraints_num
    return tasks_available


def calc_exp_times_for_action(team, task_id, action_id):
    """
    returns (time_to_start, time_to_complete) fuzzy number for expected time

    time_to_start    :: fuzzy time - expected time for prev actions & involved constraints to completed
    time_to_complete :: fuzzy time - expected time for action to complete once it has started
    None when tasks/constraints involved still not assigned
    """

    # available / inprogress / completed
    if team.current_behavior[task_id].status == 'available':
        # return None if task still unassigned
        time_to_start = None
        time_to_complete = None
        return time_to_start, time_to_complete

    elif team.current_behavior[task_id].status == 'completed':
        # return 0 if task completed
        time_to_start = fl.Fuzzy((0, 0))
        time_to_complete = fl.Fuzzy((0, 0))
        return time_to_start, time_to_complete

    elif team.current_behavior[task_id].status == 'inprogress':

        if team.current_behavior[task_id][action_id].status is None:
            # this should never happen, here only for completion
            return None, None

        elif team.current_behavior[task_id][action_id].status == 'inqueue':
            time_for_constraints_to_be_met = \
                calc_exp_time_for_constraints(team, team.current_behavior[task_id][action_id])
            time_to_complete = team.current_behavior[task_id].assigned_to.skills[action_id]['t']

            if time_for_constraints_to_be_met:

                prev_action = team.current_behavior[task_id].get_prev_action_of(action_id)
                prev_time_to_start, prev_time_to_complete = calc_exp_times_for_action(team, task_id, prev_action.id)
                if prev_time_to_start is not None:
                    time_to_complete_prev_actions = prev_time_to_start + prev_time_to_complete
                else:
                    time_to_complete_prev_actions = None

                if time_to_complete_prev_actions:
                    time_to_start = max(time_for_constraints_to_be_met, time_to_complete_prev_actions)
                    # return prediction
                    return time_to_start, time_to_complete
                else:
                    # cannot predict time for previous actions to be completed
                    return None, time_to_complete
            else:
                # cannot predict time for constraints to be met
                return None, time_to_complete

        elif team.current_behavior[task_id][action_id].status == 'inwaiting':
            time_for_constraints_to_be_met = \
                calc_exp_time_for_constraints(team, team.current_behavior[task_id][action_id])
            time_to_start = time_for_constraints_to_be_met
            time_to_complete = team.current_behavior[task_id][action_id].assigned_to.skills[action_id]['t']
            return time_to_start, time_to_complete

        elif team.current_behavior[task_id][action_id].status == 'inprogress':
            time_to_start = fl.Fuzzy((0, 0))
            time_to_complete = team.current_behavior[task_id][action_id].assigned_to.exp_time_left_action
            return time_to_start, time_to_complete

        elif team.current_behavior[task_id][action_id].status == 'completed':
            time_to_start = fl.Fuzzy((0, 0))
            time_to_complete = fl.Fuzzy((0, 0))
            return time_to_start, time_to_complete

        else:
            raise ValueError('Invalid action status')

    else:
        raise ValueError('Invalid task status')


def calc_exp_time_for_constraints(team, action):
    """
    calculates expected time for constraints of action to be met
    returns Fuzzy / None

    Fuzzy   prediction of time needed for actions' constraints to be met
    None    no prediction because of constraints belonging to unassigned tasks
    """

    constraints_times = []
    for constraint in action.constraints:
        constraining_task_id, constraining_action_id = map(int, constraint.split('-'))
        constraint_time_to_start, constraint_time_to_complete = \
            calc_exp_times_for_action(team, constraining_task_id, constraining_action_id)
        constraint_time_total = \
            constraint_time_to_start + constraint_time_to_complete if constraint_time_to_start else None
        if constraint_time_total:
            constraints_times.append(constraint_time_total)
        else:
            constraints_times = None
            break

    if constraints_times is None:
        # none means there are unpredictable constraints
        return None
    elif len(constraints_times) == 0:
        # empty list means there are no constraints
        return fl.Fuzzy((0, 0))
    else:
        # list shows expected times for each constraint to be met
        return max(constraints_times)


def calc_exp_time_to_complete_current_task(team, agent):

    if agent.current_task:
        # get id of current task
        curr_task_id = agent.current_task.id
        # get id of last action of current task
        last_action_id = agent.current_task.get_prev_action_of().id
        # get expected times (time_to_start, time_to_complete) for last action of current task
        action_time_to_start, action_time_to_complete = calc_exp_times_for_action(team, curr_task_id, last_action_id)
        if action_time_to_start:
            return action_time_to_start + action_time_to_complete
        else:
            return None
    else:
        return fl.Fuzzy((0, 0))


def calc_exp_time_to_complete_next_task(team, agent, task):

    time_needed_so_far = calc_exp_time_to_complete_current_task(team, agent)
    if time_needed_so_far is None:
        return None

    for action in task.actions:

        # ----- calc expected time for constraints of action to be met ----- #
        time_for_constraints_to_be_met = calc_exp_time_for_constraints(team, action)

        # ----- get expected time for agent to complete action once she has started it ----- #
        time_for_agent_to_complete_action = agent.skills[action.id]['t']

        # ----- calc expected time needed so far (constraints met and action completed) ----- #
        if time_for_constraints_to_be_met:
            # constraints can be met in parallel with agent working on previous actions
            time_needed_so_far = \
                max(time_needed_so_far, time_for_constraints_to_be_met) + time_for_agent_to_complete_action
        else:
            time_needed_so_far = None

        # ----- return None if action has unpredictable constraints ----- #
        if time_needed_so_far is None:
            return None

    return time_needed_so_far
