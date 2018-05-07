
from os import path
from csv import DictWriter


class Reporter:

    print_enabled = None
    export_enabled = None

    experiment_id = None
    trial_report = {}
    actions_report = {}
    agents_report = {}

    def __init__(self, settings, init_data):

        # set reporter's settings
        self.print_enabled = True if settings['print_enabled'] is True else False
        self.export_enabled = True if settings['export_enabled'] is True else False

        # set experiment params
        self.experiment_id = init_data['experiment_id']
        self.scenario_type = init_data['scenario_type']

        # init trial report
        self.trial_report = {
            'scenario_id': init_data['scenario_id'],
            'time_max': init_data['time_max'],
            'simulation_id': init_data['simulation_id'],
            'planner': init_data['planner'],
            'behavior_status': None,
            'time_spent': None,
            'robustness': None
        }

        # init actions' report
        self.actions_report = {}

        # init agents' report
        self.agents_report = {}
        for agent_id in init_data['agents_ids']:
            self.agents_report[agent_id] = []

    def report_agent_status(self, agent_id, agent_status):
        if self.print_enabled or self.export_enabled:
            self.agents_report[agent_id].append(agent_status)

    def report_action_robustness(self, task_id, action_id, robustness):
        if self.print_enabled or self.export_enabled:
            self.actions_report['%s-%s' % (task_id, action_id)] = robustness

    def report_end_of_trial(self, behavior_status, time_spent):
        if self.print_enabled or self.export_enabled:
            self.trial_report['behavior_status'] = behavior_status
            self.trial_report['time_spent'] = time_spent
            mr_per_task = {}
            for k, v in self.actions_report.items():
                task_id, _ = map(int, k.split('-'))
                if task_id not in mr_per_task:
                    mr_per_task[task_id] = v
                elif mr_per_task[task_id] > v:
                    mr_per_task[task_id] = v
            mean_mr = sum(mr_per_task.values()) / len(mr_per_task)
            self.trial_report['robustness'] = mean_mr

    def present_results(self):
        if self.print_enabled or self.export_enabled:

            # ----- trial status -----
            if self.print_enabled:
                print('\n\nBasic info :: %s' % self.trial_report)

            # ----- concurrent work -----
            timesteps = list(zip(*([status for status in self.agents_report.values()])))
            concurrency = list(map(
                lambda step: all([True if ag_step == 'work' else False for ag_step in step]),
                timesteps))

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
                    'total': len(self.agents_report[agent_id])
                }
                if agent_stats['total'] != agent_stats['rest'] + agent_stats['wait'] + agent_stats['work']:
                    raise ValueError('Unknown agents states')

                for k, v in agent_stats.items():
                    agents_stats['ag_%s_%s' % (agent_id, k)] = v

                if self.print_enabled:
                    print('Agent#%s :: %s' % (agent_id, agent_stats))

            # ----- save data to csv -----
            if self.export_enabled:

                # check if file exists
                if self.experiment_id:
                    csv_path = 'reports/experiment-%s-%s.csv' \
                               % (self.experiment_id, self.scenario_type)
                else:
                    csv_path = 'reports/generic.csv'
                file_preexists = True if path.exists(csv_path) else False

                # gather data
                data = {**self.trial_report, **concurrency_stats, **agents_stats}
                fieldnames = data.keys()

                # write data to file
                with open(csv_path, 'a', newline='') as f:
                    csv_writer = DictWriter(f, fieldnames=fieldnames)
                    if not file_preexists:
                        csv_writer.writeheader()
                    csv_writer.writerow(data)
