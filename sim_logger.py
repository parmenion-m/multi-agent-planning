
from colorama import Fore, Back


class Logger:

    print_state_basic = None
    print_state_more = None
    print_planner = None
    print_events = None

    def __init__(self, verbose_level):
        self.print_state_basic = True if verbose_level in ['basic', 'full'] else False
        self.print_state_more = True if verbose_level in ['full'] else False
        self.print_planner = True if verbose_level in ['basic', 'full'] else False
        self.print_events = True if verbose_level in ['basic', 'full'] else False

    # ---------- States ---------- #

    def state_header(self, behavior, team):
        if self.print_state_basic:

            print(' Time  | ', end='')
            for agent in team.agents:
                text = 'Agent #%i' % agent.id
                print(text.center(8), end=' | ')

            for task in behavior.tasks:
                text = 'Task #%i' % task.id
                print(text.center(len(task.actions)*5 - 1), end=' | ')

            print('Events:', end='')

    def state_row(self, behavior, team, sim_time):
        if self.print_state_basic:

            print('\n' + str(sim_time).center(6) + ' | ', end='')
            for agent in team.agents:

                if agent.status == 'rest':
                    color_start = Fore.BLUE
                    text = 'REST'
                elif agent.status == 'wait':
                    color_start = Fore.RED
                    text = '%s-%s' % (agent.current_task.id, agent.current_action.id)
                elif agent.status == 'work':
                    color_start = Fore.GREEN
                    text = '%s-%s' % (agent.current_task.id, agent.current_action.id)
                else:
                    raise ValueError('Logger: Unknown agent status')
                color_end = Fore.RESET + Back.RESET
                print(color_start + text.center(8) + color_end, end=' | ')

            for task in behavior.tasks:
                for action in task.actions:
                    if action.status is None:
                        color_start = ''
                    elif action.status == 'inqueue':
                        color_start = Fore.BLUE
                    elif action.status == 'inwaiting':
                        color_start = Fore.LIGHTYELLOW_EX
                    elif action.status == 'inprogress':
                        color_start = Fore.GREEN
                    elif action.status == 'completed':
                        color_start = Fore.LIGHTBLACK_EX
                    else:
                        raise ValueError('Logger: Unknown action status')
                    if action.constraints:
                        color_start += Back.RED
                    text = str(action.id)
                    color_end = Fore.RESET + Back.RESET
                    print(color_start + text + color_end, end=' ')
                print('| ', end='')

    def state_more_info(self, behavior, team):
        if self.print_state_more:

            # more info on agents
            for agent in team.agents:
                print()
                print('  %s [%s] %s-%s [%s-%s] %s' % (
                    agent.id,
                    agent.status,
                    agent.current_task.id if agent.current_task else None,
                    agent.current_action.id if agent.current_action else None,
                    agent.current_task.status if agent.current_task else None,
                    agent.current_action.status if agent.current_action else None,
                    agent.exp_time_left_action if agent.exp_time_left_action else None
                ), end='')

            # more info on tasks & actions
            import helpers
            for task in behavior.tasks:
                print()
                print('    %s (%s)::  ' % (task.id, task.status), end='')
                for action in task.actions:
                    print('%s (%s) %s : %s | ' % (action.id, action.status, action.constraints,
                                                  helpers.calc_exp_times_for_action(team, task.id, action.id)), end='')

    # ---------- Planner Thoughts ---------- #

    def planner_dpv2_benefit_table(self, benefit_scores):
        if self.print_planner:
            print('\nTeam Benefit Scores:', end='')
            for k, v in benefit_scores.items():
                print('\n  %s :: %s' % (k, v), end='')

    def planner_new_vanilla_table(self, vanilla_scores):
        if self.print_planner:
            print('\nVanilla Scores:', end='')
            for k, v in vanilla_scores.items():
                print('\n  %s :: %s' % (k, v), end='')

    def planner_new_values_table(self, values):
        if self.print_planner:
            print('\nValues Table:', end='')
            for k, v in values.items():
                print('\n  %s :: ' % k, end='')
                for item in v.items():
                    print('%s: %.3f  ' % (item[0], item[1]), end='')

    def planner_assignments(self, assignments):
        if self.print_planner:
            print('\nAssignments: %s' % assignments)

    # ---------- Behavior Events ---------- #

    def behavior_completed(self, behavior_id):
        if self.print_events:
            print('Behavior %s completed' % behavior_id, end=' / ')

    # ---------- Task Events ---------- #

    def task_completed(self, task_id):
        if self.print_events:
            print('Task %s completed' % task_id, end=' / ')

    # ---------- Action Events ---------- #

    def action_available(self, action_id):
        if self.print_events:
            print('Action %s is now available' % action_id, end=' / ')

    def action_completed(self, action_id):
        if self.print_events:
            print('Action %s completed' % action_id, end=' / ')

    # ---------- Team Events ---------- #

    # ---------- Agent Events ---------- #

    def agent_assigned_task(self, agent_id, task_id):
        if self.print_events:
            print('Agent %s assigned to Task %s' % (agent_id, task_id), end=' / ')

    def agent_assigned_action(self, agent_id, task_id, action_id, action_status):
        if self.print_events:
            print('Agent %s self-assigned to Action %s-%s (%s)'
                  % (agent_id, task_id, action_id, action_status), end=' / ')

    def agent_started_working(self, agent_id, task_id, action_id):
        if self.print_events:
            print('Agent %s started working on Action %s-%s' % (agent_id, task_id, action_id), end=' / ')

    def agent_at_rest(self, agent_id):
        if self.print_events:
            print('Agent %s is at rest' % agent_id, end=' / ')
