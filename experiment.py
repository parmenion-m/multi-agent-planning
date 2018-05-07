
from simulation import Simulation

import random


class Experiment:

    id = None
    scenario_type = None
    num_of_scenarios = None
    num_of_simulations = None
    planners = None

    def __init__(self, settings):

        # ----- init experiment -----
        self.id = settings['experiment_id']
        self.scenario_type = settings['scenario_type']
        self.num_of_scenarios = settings['num_of_scenarios']
        self.num_of_simulations = settings['num_of_simulations']
        self.planners = settings['planners']

    def __call__(self):

        # ----- run experiment -----
        random.seed(self.id)
        scenario_ids = random.sample(range(1000000, 9999999), k=self.num_of_scenarios) \
            if self.scenario_type.split('_')[0] == 'custom' else [None]
        simulation_ids = random.sample(range(100000, 999999), k=self.num_of_simulations)

        print('Experiment started ...')

        trial_num = 0

        for scenario_id in scenario_ids:

            for simulation_id in simulation_ids:

                for planner in self.planners:

                    # ----- init simulation -----
                    sim_settings = {
                        'experiment_id': self.id,
                        'scenario_type': self.scenario_type,
                        'scenario_id': scenario_id,
                        'simulation_id': simulation_id,
                        'planner': planner,
                        'logger_verbose_level': False,
                        'reporter_print': False,
                        'reporter_export': True,
                    }

                    # todo skip if row exists - place exp size in filename

                    trial_num += 1
                    if trial_num % 100 == 0:
                        print('Starting trial #%s ...' % trial_num)

                    # ----- run simulation -----
                    Simulation(sim_settings)()


if __name__ == "__main__":

    # ----- prepare settings -----
    experiment_settings = {
        'experiment_id': 1000,
        'scenario_type': 'custom_3_10',     # salad / cereal / custom_2_7 (agents, tasks)
        'num_of_scenarios': 100,            # num of different scenarios to be generated (custom scenarios only)
        'num_of_simulations': 10,           # num of times each scenario to be run
        'planners': ['base', 'base+', 'dpv1', 'dpv2', 'new-0.0', 'new-0.5', 'new-1.0'],
    }

    # ----- run experiment -----
    Experiment(experiment_settings)()
