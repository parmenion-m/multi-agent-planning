
from model import Behavior, Team
from scenarios import Scenario
from sim_logger import Logger
from sim_reporter import Reporter
# from planners import Planners


class Simulation:

    time = None
    timestep = None
    max_time = None

    scenario_id = None
    behavior = None
    team = None

    logger = None
    reporter = None

    def __init__(self, settings):

        # init time
        self.time = 0.0
        self.timestep = settings['timestep']
        self.max_time = settings['max_time']

        # init logger
        self.logger = Logger({'verbose': settings['logger_verbose']})

        # init reporter
        agents_ids = [agent_specs['id'] for agent_specs in settings['team_specs']['agents_specs']]
        self.reporter = Reporter({'verbose': settings['reporter_verbose']}, agents_ids)

        # init behavior & team
        self.scenario_id = settings['scenario_id']
        self.behavior = Behavior(settings['behavior_specs'], settings['actions_names'], self.logger)
        self.team = Team(settings['team_specs'], self.logger, self.reporter)

    def __call__(self):

        # --- assign behavior to team ---
        self.team.assign_behavior(self.behavior)

        # --- print starting state ---
        self.logger.state_header(self.behavior, self.team)
        self.logger.state_row(self.behavior, self.team, self.time)

        while self.behavior.status == 'inprogress' and self.time < self.max_time:

            # --- make progress ---
            self.team.progress(self.timestep)

            # --- update clock ---
            self.time = round(self.time + self.timestep, 1)

            # --- print new state ---
            self.logger.state_row(self.behavior, self.team, self.time)

        # --- report job's outcome ---
        self.reporter.report_behavior_status(self.scenario_id, self.behavior.status, self.time)

        # --- print report ---
        self.reporter.print_report()


if __name__ == '__main__':

    # ----- select a scenario -----
    scenario_id = 1000  # 'salad_preparation'

    if scenario_id == 'salad_preparation':
        # ----- use the salad preparation scenario -----
        actions_names, behavior_specs, team_specs = Scenario().salad_preparation()
        max_time = Scenario().calc_no_concurrency_worst_time(behavior_specs, team_specs)
    else:
        # ----- use a randomly generated scenario -----
        actions_names, behavior_specs, team_specs = Scenario().generic(scenario_id)
        max_time = Scenario().calc_no_concurrency_worst_time(behavior_specs, team_specs)

    # ----- prepare settings -----
    sim_settings = {
        'scenario_id': scenario_id,
        'actions_names': actions_names,
        'behavior_specs': behavior_specs,
        'team_specs': team_specs,
        'max_time': max_time,
        'timestep': 1.0,
        'logger_verbose': True,
        'reporter_verbose': True
    }

    # ----- run simulation -----
    Simulation(sim_settings)()
