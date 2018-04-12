
from model import Behavior, Team
from sim_logger import Logger
from scenarios import Scenario


class Simulation:

    time = None
    timestep = None
    max_time = None

    logger = None

    behavior = None
    team = None

    def __init__(self, settings):

        # init time
        self.time = 0.0
        self.timestep = settings['timestep']
        self.max_time = settings['max_time']

        # init logger
        self.logger = Logger({'verbose': settings['logger_verbose']})

        # init behavior & team
        self.behavior = Behavior(settings['behavior_specs'], settings['actions_names'], self.logger)
        self.team = Team(settings['team_specs'], self.logger)

    def __call__(self):

        # --- assign behavior to team ---
        self.team.assign_behavior(self.behavior)

        # --- print starting state ---
        self.logger.state_header(self.behavior, self.team)
        self.logger.state_row(self.behavior, self.team, self.time)

        while self.behavior.status == 'inprogress' and self.team.status == 'work' and self.time < self.max_time:

            # --- make progress ---
            self.team.progress(self.timestep)

            # --- update clock ---
            self.time = round(self.time + self.timestep, 1)

            # --- print new state ---
            self.logger.state_row(self.behavior, self.team, self.time)


if __name__ == '__main__':

    # ----- create scenario -----
    actions_names, behavior_specs, team_specs = Scenario().salad_preparation()
    # actions_names, behavior_specs, team_specs = Scenario().generic()
    max_time = Scenario().calc_no_concurrency_worst_time(behavior_specs, team_specs)

    # ----- prepare settings -----
    sim_settings = {
        'actions_names': actions_names,
        'behavior_specs': behavior_specs,
        'team_specs': team_specs,
        'max_time': max_time,
        'timestep': 1.0,
        'logger_verbose': True
    }

    # ----- run simulation -----
    Simulation(sim_settings)()
