
from colorama import Fore, Back


class Logger:

    verbose = None

    def __init__(self, settings):
        self.verbose = True if settings['verbose'] is True else False

    # ---------- States ---------- #

    def state_header(self, behavior, team):
        if self.verbose:

            print(' Time  | ', end='')
            for agent in team.agents:
                text = 'Agent #%i' % agent.id
                print(text.center(8), end=' | ')

            for task in behavior.tasks:
                text = 'Task #%i' % task.id
                print(text.center(len(task.actions)*5 - 1), end=' | ')

            print('Events:', end='')

    def state_row(self, behavior, team, sim_time):
        if self.verbose:

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
                    if action.status == 'available':
                        color_start = Fore.BLUE
                    elif action.status == 'constrained':
                        color_start = Fore.RED
                    elif action.status == 'inprogress':
                        color_start = Fore.GREEN
                    elif action.status == 'completed':
                        color_start = Fore.LIGHTBLACK_EX
                    else:
                        raise ValueError('Logger: Unknown task status')
                    text = str(action.id)
                    color_end = Fore.RESET + Back.RESET
                    print(color_start + text + color_end, end=' ')
                print('| ', end='')

    # ---------- Behavior Events ---------- #

    def behavior_completed(self, behavior_id):
        if self.verbose:
            print('Behavior %s completed' % behavior_id, end=' / ')

    # ---------- Task Events ---------- #

    def task_completed(self, task_id):
        if self.verbose:
            print('Task %s completed' % task_id, end=' / ')

    # ---------- Action Events ---------- #

    def action_available(self, action_id):
        if self.verbose:
            print('Action %s is now available' % action_id, end=' / ')

    def action_completed(self, action_id):
        if self.verbose:
            print('Action %s completed' % action_id, end=' / ')

    # ---------- Team Events ---------- #

    # ---------- Agent Events ---------- #

    def agent_assigned_task(self, agent_id, task_id):
        if self.verbose:
            print('Agent %s assigned to Task %s' % (agent_id, task_id), end=' / ')

    def agent_assigned_action(self, agent_id, task_id, action_id, action_status):
        if self.verbose:
            print('Agent %s self-assigned to Action %s-%s (%s)' % (agent_id, task_id, action_id, action_status), end=' / ')

    def agent_started_working(self, agent_id, task_id, action_id):
        if self.verbose:
            print('Agent %s started working on Action %s-%s' % (agent_id, task_id, action_id), end=' / ')

    def agent_at_rest(self, agent_id):
        if self.verbose:
            print('Agent %s is at rest' % agent_id, end=' / ')

    # ---------- Other ---------- #

    def newline(self):
        if self.verbose:
            print()
