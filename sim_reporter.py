
from os import path
from csv import DictWriter


class Reporter:

    print_enabled = None
    export_enabled = None

    experiment_id = None
    behavior_report = {}
    agents_report = {}
    actions_report = {}

    def __init__(self, settings, init_data):

        # set reporter's settings
        self.print_enabled = True if settings['print_enabled'] is True else False
        self.export_enabled = True if settings['export_enabled'] is True else False

        # set experiment id
        self.experiment_id = init_data['experiment_id']

        # init behavior report
        self.behavior_report = {
            'simulation_id': init_data['simulation_id'],
            'scenario_id': init_data['scenario_id'],
            'scenario_type': init_data['scenario_type'],
            'time_max': init_data['time_max'],
            'planner': init_data['planner'],
            'behavior_status': None,
            'time_spent': None,
            'mean_robustness': None
        }

        # init agents' reports
        for agent_id in init_data['agents_ids']:
            self.agents_report[agent_id] = []

    def report_agent_status(self, agent_id, agent_status):

        self.agents_report[agent_id].append(agent_status)

    def report_action_robustness(self, task_id, action_id, robustness):

        self.actions_report['%s-%s' % (task_id, action_id)] = robustness

    def report_behavior_status(self, behavior_status, time_spent):

        self.behavior_report['behavior_status'] = behavior_status
        self.behavior_report['time_spent'] = time_spent
        self.behavior_report['mean_robustness'] = sum(self.actions_report.values()) / len(self.actions_report)

    def create_report(self):

        # ----- behavior status -----
        if self.print_enabled:
            print('\n\nBehavior :: %s' % self.behavior_report)

        # ----- concurrent work -----
        timesteps = list(zip(*([status for status in self.agents_report.values()])))
        concurrency = list(map(lambda step: all([True if ag_step == 'work' else False for ag_step in step]), timesteps))

        concurrency_stats = {
            'concurrency_true': concurrency.count(True),
            'concurrency_false': concurrency.count(False)
        }
        if self.print_enabled:
            print('Concurrency :: %s' % concurrency_stats)

        # ----- agents' stats -----
        agents_stats = {}
        for agent_id in self.agents_report.keys():
            agent_stats = {
                'rest': self.agents_report[agent_id].count('rest'),
                'wait': self.agents_report[agent_id].count('wait'),
                'work': self.agents_report[agent_id].count('work'),
                'sleep': self.agents_report[agent_id].count('sleep'),
                'total': len(self.agents_report[agent_id])
            }
            if self.print_enabled:
                print('Agent#%s :: %s' % (agent_id, agent_stats))

            for k, v in agent_stats.items():
                agents_stats['ag_%s_%s' % (agent_id, k)] = v

        # ----- save data to csv -----
        if self.export_enabled:

            # check if file exists
            if self.experiment_id:
                csv_path = 'reports/experiment_%s_%s.csv' % (self.experiment_id, self.behavior_report['scenario_type'])
            else:
                csv_path = 'reports/generic.csv'
            file_preexists = True if path.exists(csv_path) else False

            # gather data
            data = {**self.behavior_report, **concurrency_stats, **agents_stats}
            fieldnames = data.keys()

            # write data to file
            with open(csv_path, 'a', newline='') as f:
                csv_writer = DictWriter(f, fieldnames=fieldnames)
                if not file_preexists:
                    csv_writer.writeheader()
                csv_writer.writerow(data)
