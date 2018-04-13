
class Reporter:

    verbose = None

    agents_report = {}
    behavior_report = {}

    def __init__(self, settings, agents_ids):

        self.verbose = True if settings['verbose'] is True else False
        for agent_id in agents_ids:
            self.agents_report[agent_id] = []

    def report_agent_status(self, agent_id, agent_status):

        self.agents_report[agent_id].append(agent_status)

    def report_behavior_status(self, scenario_id, behavior_status, time_spent):

        self.behavior_report = {
            'scenario_id': scenario_id,
            'behavior_status': behavior_status,
            'time_spent': time_spent
        }

    def print_report(self):

        if self.verbose:
            print()
            print()

            # ----- agents' stats -----
            for agent_id in self.agents_report.keys():
                agent_stats = {
                    'rest': self.agents_report[agent_id].count('rest'),
                    'wait': self.agents_report[agent_id].count('wait'),
                    'work': self.agents_report[agent_id].count('work'),
                    'sleep': self.agents_report[agent_id].count('sleep'),
                    'total': len(self.agents_report[agent_id])
                }
                print('Agent#%s :: %s' % (agent_id, agent_stats))
            print()

            # ----- concurrent work -----
            timesteps = list(zip(*([status for status in self.agents_report.values()])))
            concurrency = list(map(lambda step: all([True if ag_step == 'work' else False for ag_step in step]), timesteps))

            concurrency_stats = {
                True: concurrency.count(True),
                False: concurrency.count(False)
            }
            print('Concurrency :: %s' % concurrency_stats)

            # ----- behavior end-status -----
            print('Behavior :: %s' % self.behavior_report)
