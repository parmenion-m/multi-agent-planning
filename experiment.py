
from simulation import Simulation

import random


class Experiment:

    id = None
    scenario_type = None
    num_of_trials = None
    planners = None

    def __init__(self, settings):

        # ----- init experiment -----
        self.id = settings['experiment_id']
        self.scenario_type = settings['scenario_type']
        self.num_of_trials = settings['num_of_trials']
        self.planners = settings['planners']

    def __call__(self):

        # ----- run experiment -----
        random.seed(self.id)
        simulation_ids = random.sample(range(10000000), k=self.num_of_trials)

        for i, simulation_id in enumerate(simulation_ids):

            if i % 100 == 0:
                print('Starting Trial #%i' % i)

            for planner in self.planners:

                # ----- init simulation -----
                sim_settings = {
                    'experiment_id': self.id,
                    'simulation_id': simulation_id,
                    'scenario_id': simulation_id,
                    'scenario_type': self.scenario_type,
                    'planner': planner,
                    'logger_verbose': False,
                    'reporter_print': False,
                    'reporter_export': True,
                }

                # ----- run simulation -----
                Simulation(sim_settings)()


if __name__ == "__main__":

    # ----- prepare settings -----
    experiment_settings = {
        'experiment_id': 5000,
        'scenario_type': 'generic_2_7_16',  # salad / generic_2_7_16  (agents, tasks, actions)
        'num_of_trials': 1000,
        'planners': ['dpv1', 'random'],
    }

    # ----- run experiment -----
    Experiment(experiment_settings)()
