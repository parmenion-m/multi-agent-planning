
from model import Behavior, Team
from sim_logger import Logger
import salad_preparation


class Simulation:

    time = None
    timestep = None

    logger = None

    behavior = None
    team = None

    def __init__(self, settings):

        # init time
        self.time = 0.0
        self.timestep = settings['timestep']

        # init logger
        self.logger = Logger({'verbose': settings['logger_verbose']})

        # init behavior & team based on scenario
        actions_names, behavior_specs, team_specs = settings['scenario']
        self.behavior = Behavior(behavior_specs, actions_names, self.logger)
        self.team = Team(team_specs, self.logger)

    def __call__(self):

        # --- assign behavior to team ---
        self.team.assign_behavior(self.behavior)

        # --- print starting state ---
        self.logger.state_header(self.behavior, self.team)
        self.logger.state_row(self.behavior, self.team, self.time)

        while self.behavior.status == 'inprogress' and self.team.status == 'work' and self.time < 300:

            # --- make progress ---
            self.team.progress(self.timestep)

            # --- update clock ---
            self.time = round(self.time + self.timestep, 1)

            # --- print new state ---
            self.logger.state_row(self.behavior, self.team, self.time)


if __name__ == '__main__':

    sim_settings = {
        'scenario': salad_preparation.get_scenario(),
        'logger_verbose': True,
        'timestep': 1.0
    }

    Simulation(sim_settings)()
