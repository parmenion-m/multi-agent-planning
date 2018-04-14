
from scenarios import Scenario
from model import Behavior, Team
from planners import *
from sim_logger import Logger
from sim_reporter import Reporter

import random


class Simulation:

    time = None
    time_step = None
    time_max = None

    behavior = None
    team = None

    planner = None
    logger = None
    reporter = None

    def __init__(self, settings):

        # ----- init rng -----
        if settings['scenario_id']:
            random.seed(settings['scenario_id'])

        # ----- create scenario -----
        if settings['scenario_type'] == 'salad':
            # use the salad preparation scenario
            actions_names, behavior_specs, team_specs = Scenario().salad_preparation()
            time_max = Scenario().calc_no_concurrency_worst_time(behavior_specs, team_specs)
        else:
            sc_params = settings['scenario_type'].split('_')
            if sc_params[0] == 'generic':
                # use a randomly generated scenario
                actions_names, behavior_specs, team_specs = Scenario().generic(
                    num_of_agents=int(sc_params[1]),
                    num_of_tasks=int(sc_params[2]),
                    num_of_actions=int(sc_params[3]))
                time_max = Scenario().calc_no_concurrency_worst_time(behavior_specs, team_specs)
            else:
                raise ValueError('Invalid scenario_type: `%s`' % settings['scenario_type'])

        # ----- init planner -----
        if settings['planner'] == 'dpv1':
            self.planner = daisy_planner_v1
        elif settings['planner'] == 'random':
            self.planner = random_planner
        else:
            raise ValueError('Unknown planner')

        # ----- init logger -----
        logger_settings = {
            'verbose': settings['logger_verbose']
        }
        self.logger = Logger(logger_settings)

        # ----- init reporter -----
        reporter_settings = {
            'print_enabled': settings['reporter_print'],
            'export_enabled': settings['reporter_export']
        }
        reporter_init_data = {
            'experiment_id': settings['experiment_id'],
            'scenario_id': settings['scenario_id'],
            'scenario_type': settings['scenario_type'],
            'planner': settings['planner'],
            'time_max': time_max,
            'agents_ids': [agent_specs['id'] for agent_specs in team_specs['agents_specs']],
        }
        self.reporter = Reporter(reporter_settings, reporter_init_data)

        # ----- init behavior & team -----
        self.scenario_id = settings['scenario_id']
        self.behavior = Behavior(behavior_specs, actions_names, self.logger)
        self.team = Team(team_specs, self.planner, self.logger, self.reporter)

        # ----- init time -----
        self.time = 0.0
        self.time_step = 1.0
        self.time_max = time_max

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
            self.logger.state_row(self.behavior, self.team, self.time)

        # ----- report job's outcome -----
        self.reporter.report_behavior_status(self.behavior.status, self.time)

        # ----- print report -----
        self.reporter.create_report()


if __name__ == '__main__':

    # ----- prepare settings -----
    sim_settings = {
        'experiment_id': None,
        'scenario_id': None,

        'scenario_type': 'salad',   # salad / generic_2_7_16  (agents, tasks, actions)
        'planner': 'dpv1',          # dpv1 / random
        'logger_verbose': True,
        'reporter_print': True,
        'reporter_export': True,
    }

    # ----- run simulation -----
    Simulation(sim_settings)()
