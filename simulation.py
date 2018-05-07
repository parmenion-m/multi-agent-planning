
from scenario import Scenario
from model import Behavior, Team
from sim_logger import Logger
from sim_reporter import Reporter

import random


class Simulation:

    simulation_id = None
    scenario_type = None
    scenario_id = None

    time = None
    time_step = None
    time_max = None

    behavior = None
    team = None

    logger = None
    reporter = None

    def __init__(self, settings):

        # ----- init simulator -----
        self.simulation_id = settings['simulation_id'] if settings['simulation_id'] else random.randint(1000, 9999)
        self.time = 0.0
        self.time_step = 1.0
        random.seed(self.simulation_id)

        # ----- create scenario -----
        scenario = Scenario(settings['scenario_type'], settings['scenario_id'])
        self.scenario_type = scenario.scenario_type
        self.scenario_id = scenario.scenario_id
        self.time_max = scenario.time_max

        # ----- init logger -----
        self.logger = Logger(settings['logger_verbose_level'])

        # ----- init reporter -----
        reporter_settings = {
            'print_enabled': settings['reporter_print'],
            'export_enabled': settings['reporter_export']
        }
        reporter_init_data = {
            'experiment_id': settings['experiment_id'],
            'scenario_type': self.scenario_type,
            'scenario_id': self.scenario_id,
            'time_max': self.time_max,
            'simulation_id': self.simulation_id,
            'planner': settings['planner'],
            'agents_ids': [agent_specs['id'] for agent_specs in scenario.team_specs['agents_specs']],
        }
        self.reporter = Reporter(reporter_settings, reporter_init_data)

        # ----- init behavior & team -----
        self.behavior = Behavior(scenario.behavior_specs, scenario.actions_names, self.logger)
        self.team = Team(scenario.team_specs, settings['planner'], self.logger, self.reporter)

    def __call__(self):

        # ----- assign behavior to team -----
        self.team.assign_behavior(self.behavior)

        # ----- print starting state -----
        self.logger.state_header(self.behavior, self.team)
        self.logger.state_row(self.behavior, self.team, self.time)

        while self.behavior.status == 'inprogress' and self.time < self.time_max:

            # ----- make progress -----
            self.team.progress(self.time_step)

            # ----- update clock -----
            self.time = round(self.time + self.time_step, 1)

            # ----- print new state -----
            self.logger.state_more_info(self.behavior, self.team)
            self.logger.state_row(self.behavior, self.team, self.time)

        # ----- report job's outcome -----
        self.reporter.report_end_of_trial(self.behavior.status, self.time)

        # ----- print report -----
        self.reporter.present_results()


if __name__ == '__main__':

    # ----- prepare settings -----
    simulation_settings = {
        'experiment_id': None,
        'scenario_type': 'custom_3_10',         # salad / cereal / custom_2_7 (agents, tasks)
        'scenario_id': 1000,
        'simulation_id': 1000,
        'planner': 'new-0.5',                   # base / base+ / dpv1 / dpv2 / new-0.0 / new-0.5 / new-1.0
        'logger_verbose_level': 'basic',        # False / basic / full
        'reporter_print': True,
        'reporter_export': True,
    }

    # ----- run simulation -----
    Simulation(simulation_settings)()
