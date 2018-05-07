
import random


class Scenario:

    scenario_type = None
    scenario_id = None

    actions_names = None
    behavior_specs = None
    team_specs = None
    time_max = None

    def __init__(self, scenario_type, scenario_id):

        self.scenario_type = scenario_type
        self.scenario_id = None if self.scenario_type in ['salad', 'cereal'] else scenario_id

        if scenario_type == 'salad':
            # return the salad preparation scenario
            self.actions_names, self.behavior_specs, self.team_specs = self.salad_preparation()
            self.time_max = self.calc_no_concurrency_worst_time(self.behavior_specs, self.team_specs)

        elif scenario_type == 'cereal':
            # return the cereal preparation scenario
            self.actions_names, self.behavior_specs, self.team_specs = self.cereal_preparation()
            self.time_max = self.calc_no_concurrency_worst_time(self.behavior_specs, self.team_specs)

        else:
            sn_params = scenario_type.split('_')
            if len(sn_params) == 3 and sn_params[0] == 'custom':
                # return a randomly generated scenario
                self.actions_names, self.behavior_specs, self.team_specs = self.custom(
                    scenario_id=scenario_id,
                    num_of_agents=int(sn_params[1]),
                    num_of_tasks=int(sn_params[2]))
                self.time_max = self.calc_no_concurrency_worst_time(self.behavior_specs, self.team_specs)

            else:
                raise ValueError('Invalid scenario_type: `%s`' % scenario_type)

    def __call__(self):
        return self.actions_names, self.behavior_specs, self.team_specs, self.time_max

    # -------------------- #

    @staticmethod
    def salad_preparation():

        actions_names = {
            1001: 'Go to cupboard',
            1002: 'Go to countertop',
            2001: 'Get salad',
            2002: 'Get salad bowl',
            2003: 'Get olive oil bottle',
            2004: 'Get mixing tool',
            3001: 'Place salad on countertop',
            3002: 'Place salad bowl on countertop',
            3003: 'Place olive oil bottle on countertop',
            3004: 'Place mixing tool on countertop',
            4001: 'Put salad in bowl',
            4002: 'Put olive oil in salad',
            5001: 'Release salad container',
            5002: 'Release olive oil bottle',
            5003: 'Release mixing tool',
            6001: 'Mix salad',
        }

        behavior_specs = {

            'id': 0,
            'name': 'Make a Salad!',
            'tasks_specs': [
                {'id': 101, 'name': 'Place salad on countertop', 'action_list': [1001, 2001, 1002, 3001],
                 'constraints': {}},  # {2001: ['105-4001']}},  NOTE: use this to create a constraints loop
                {'id': 102, 'name': 'Place salad bowl on countertop', 'action_list': [1001, 2002, 1002, 3002],
                 'constraints': {}},
                {'id': 103, 'name': 'Place olive oil bottle on countertop', 'action_list': [1001, 2003, 1002, 3003],
                 'constraints': {}},
                {'id': 104, 'name': 'Place mixing tool on countertop', 'action_list': [1001, 2004, 1002, 3004],
                 'constraints': {}},
                {'id': 105, 'name': 'Put salad in bowl', 'action_list': [2001, 4001, 5001],
                 'constraints': {2001: ['101-3001', '102-3002', '103-3003', '104-3004']}},
                {'id': 106, 'name': 'Put olive oil in salad', 'action_list': [2003, 4002, 5002],
                 'constraints': {2003: ['105-4001']}},
                {'id': 107, 'name': 'Mix salad', 'action_list': [2004, 6001, 5003],
                 'constraints': {2004: ['105-4001', '106-4002']}},
            ]
        }

        team_specs = {

            'id': 0,
            'name': 'SaladBots',
            'agents_specs': [

                {
                    'id': 0,
                    'name': 'Robot-1',
                    'skills': {
                        1001: {'t': (21, 32),   'r': 9},
                        1002: {'t': (21, 32),   'r': 9},
                        2001: {'t': (4, 9),     'r': 9},
                        2002: {'t': (6, 9),     'r': 9},
                        2003: {'t': (4, 8),     'r': 9},
                        2004: {'t': (3, 8),     'r': 9},
                        3001: {'t': (3, 7),     'r': 9},
                        3002: {'t': (4, 7),     'r': 9},
                        3003: {'t': (3, 5),     'r': 9},
                        3004: {'t': (4, 6),     'r': 9},
                        4001: {'t': (7, 10),    'r': 9},
                        4002: {'t': (5, 8),     'r': 9},
                        5001: {'t': (2, 4),     'r': 9},
                        5002: {'t': (3, 5),     'r': 9},
                        5003: {'t': (3, 5),     'r': 9},
                        6001: {'t': (5, 11),    'r': 9},
                    }
                },

                {
                    'id': 1,
                    'name': 'Robot-2',
                    'skills': {
                        1001: {'t': (22, 38),   'r': 9},
                        1002: {'t': (22, 38),   'r': 9},
                        2001: {'t': (6, 10),    'r': 7},
                        2002: {'t': (7, 10),    'r': 5},
                        2003: {'t': (7, 10),    'r': 7},
                        2004: {'t': (5, 9),     'r': 7},
                        3001: {'t': (4, 8),     'r': 7},
                        3002: {'t': (5, 7),     'r': 7},
                        3003: {'t': (3, 6),     'r': 7},
                        3004: {'t': (3, 8),     'r': 5},
                        4001: {'t': (7, 12),    'r': 7},
                        4002: {'t': (5, 7),     'r': 9},
                        5001: {'t': (3, 6),     'r': 9},
                        5002: {'t': (3, 6),     'r': 9},
                        5003: {'t': (3, 8),     'r': 9},
                        6001: {'t': (6, 14),    'r': 7},
                    }
                }
            ]
        }

        return actions_names, behavior_specs, team_specs

    # -------------------- #

    @staticmethod
    def cereal_preparation():

        actions_names = {
            1001: 'Move close to bowl',
            1002: 'Move close to cereals box',
            1003: 'Move close to milk box',
            1004: 'Move close to whisk',
            1005: 'Move close to table',
            1006: 'Move close to cupboard',
            2001: 'Get bowl',
            2002: 'Get cereals box',
            2003: 'Get milk box',
            2004: 'Get whisk',
            3001: 'Place bowl on the right table position',
            3002: 'Put cereals on table',
            4001: 'Pour cereals in bowl',
            4002: 'Pour milk in bowl',
            5001: 'Release cereals box',
            5002: 'Release milk box',
            5003: 'Release whisk',
            6001: 'Mix bowl content',
        }

        behavior_specs = {

            'id': 0,
            'name': 'Make Breakfast!',
            'tasks_specs': [
                {'id': 101, 'name': 'Place bowl on table', 'action_list': [1001, 2001, 1005, 3001],
                 'constraints': {}},
                {'id': 102, 'name': 'Put cereals on table', 'action_list': [1002, 2002, 1005, 3002],
                 'constraints': {}},
                {'id': 103, 'name': 'Pour cereals in bowl', 'action_list': [2002, 4001, 5001],
                 'constraints': {2002: ['101-3001', '102-3002']}},
                {'id': 104, 'name': 'Pour milk in bowl', 'action_list': [2003, 4002, 5002],
                 'constraints': {2003: ['101-3001']}},
                {'id': 105, 'name': 'Mix bowl content', 'action_list': [1004, 2004, 2001, 6001, 3001, 5003],
                 'constraints': {2004: ['103-4001', '104-4002']}},
                {'id': 106, 'name': 'Place milk box on cupboard', 'action_list': [1003, 2003, 1006, 5002],
                 'constraints': {2003: ['104-5002']}},
            ]
        }

        team_specs = {

            'id': 0,
            'name': 'CerealBots',
            'agents_specs': [

                {
                    'id': 0,
                    'name': 'Armar-4',
                    'skills': {
                        1001: {'t': (0, 2),     'e': 1},
                        1002: {'t': (22, 38),   'e': 7},
                        1003: {'t': (0, 3),     'e': 1},
                        1004: {'t': (0, 2),     'e': 1},
                        1005: {'t': (0, 2),     'e': 1},
                        1006: {'t': (35, 47),   'e': 7},
                        2001: {'t': (16, 34),   'e': 3},
                        2002: {'t': (21, 35),   'e': 3},
                        2003: {'t': (14, 31),   'e': 3},
                        2004: {'t': (20, 33),   'e': 3},
                        3001: {'t': (12, 23),   'e': 3},
                        3002: {'t': (9, 22),    'e': 3},
                        4001: {'t': (5, 12),    'e': 1},
                        4002: {'t': (6, 23),    'e': 1},
                        5001: {'t': (9, 22),    'e': 3},
                        5002: {'t': (6, 17),    'e': 3},
                        5003: {'t': (14, 27),   'e': 3},
                        6001: {'t': (11, 20),   'e': 3},
                    }
                },

                {
                    'id': 1,
                    'name': 'Armar-3a',
                    'skills': {
                        1001: {'t': (8, 12),    'e': 1},
                        1002: {'t': (6, 12),    'e': 1},
                        1003: {'t': (1, 8),     'e': 1},
                        1004: {'t': (8, 15),    'e': 1},
                        1005: {'t': (8, 12),    'e': 1},
                        1006: {'t': (13, 21),   'e': 3},
                        2001: {'t': (23, 35),   'e': 3},
                        2002: {'t': (26, 42),   'e': 3},
                        2003: {'t': (11, 25),   'e': 3},
                        2004: {'t': (23, 34),   'e': 5},
                        3001: {'t': (12, 18),   'e': 3},
                        3002: {'t': (27, 46),   'e': 3},
                        4001: {'t': (13, 25),   'e': 3},
                        4002: {'t': (12, 21),   'e': 3},
                        5001: {'t': (9, 21),    'e': 3},
                        5002: {'t': (23, 42),   'e': 3},
                        5003: {'t': (16, 27),   'e': 3},
                        6001: {'t': (13, 25),   'e': 3},
                    }
                }
            ]
        }

        return actions_names, behavior_specs, team_specs

    # -------------------- #

    @staticmethod
    def custom(scenario_id, num_of_agents=2, num_of_tasks=7):

        # init rng for scenario generation
        # without messing with simulation's rng state
        prev_rng_state = random.getstate()
        random.seed(scenario_id)

        if not (isinstance(num_of_agents, int) and isinstance(num_of_tasks, int)
                and num_of_agents > 0 and num_of_tasks > 0):
            raise ValueError('Invalid scenario settings')

        # ----- Actions -----
        num_of_actions = num_of_tasks * 4
        actions_ids = random.sample(range(1000, 8999), num_of_actions - num_of_tasks)
        sp_actions_ids = random.sample(range(9000, 9999), num_of_tasks)
        actions_names = {}
        actions_times = {}      # basic duration for action, varied later by agent's skill
        for i in actions_ids + sp_actions_ids:
            actions_names[i] = 'Action#%s' % i
            actions_times[i] = random.randint(5, 15)

        # ----- Agents & Skills -----
        agents_specs = []
        for i in range(num_of_agents):
            agent_skills = {}
            for action_id, action_base_time in actions_times.items():
                range_modifier = random.choice([0.1, 0.2, 0.3, 0.4])
                extra_modifier = random.choice([0, 1, 2, 3])
                duration_min = int(action_base_time * (1-range_modifier)) + extra_modifier
                duration_max = int(action_base_time * (1+range_modifier)) + extra_modifier
                if action_id < 5000:
                    robustness = 9
                elif action_id < 9000:
                    robustness = random.choice([7, 9])
                else:
                    robustness = 9 - extra_modifier
                agent_skills[action_id] = {'t': (duration_min, duration_max), 'r': robustness}

            agent_specs = {
                'id': i,
                'name': 'Agent#%s' % i,
                'skills': agent_skills
            }
            agents_specs.append(agent_specs)

        # ----- Team -----
        team_specs = {
            'id': 0,
            'name': 'Team#%s' % 0,
            'agents_specs': agents_specs
        }

        # ----- Tasks & Constraints -----
        tasks_specs = []
        for task_id in range(101, 101 + num_of_tasks):

            constraints = []
            constraints_num = min(random.choice([0, 0, 1, 3, 5]), len(tasks_specs))
            constraining_tasks = random.sample([task['id'] for task in tasks_specs], constraints_num)
            for constraining_task in constraining_tasks:
                t_actions = []
                for t in tasks_specs:
                    if t['id'] == constraining_task:
                        t_actions = t['action_list']
                        break
                constraining_action = random.choice(t_actions)
                constraints.append('%s-%s' % (constraining_task, constraining_action))

            action_list = random.sample(actions_ids, min(random.randint(3, 6), len(actions_ids)))
            action_list.append(random.choice(sp_actions_ids))
            random.shuffle(action_list)
            task_spec = {
                'id': task_id,
                'name': 'Task#%s' % task_id,
                'action_list': action_list,
                'constraints': {random.choice(action_list): constraints} if constraints else {}
            }
            tasks_specs.append(task_spec)

        # ----- Behavior -----
        behavior_id = 0
        behavior_specs = {
            'id': behavior_id,
            'name': 'Behavior#%s' % behavior_id,
            'tasks_specs': tasks_specs
        }

        # restore rng state
        random.setstate(prev_rng_state)

        return actions_names, behavior_specs, team_specs

    # -------------------- #

    @staticmethod
    def calc_no_concurrency_worst_time(behavior_specs, team_specs):
        """
        calculate the maximum time that it would take a team to complete a behavior
        this assumes that:
        (1) for each action the less skilled agent is chosen to perform it
        (2) the agent selected needs the maximum time possible in order to complete it
        (3) no concurrency happens
        """
        worst_case_time = 0
        for task_specs in behavior_specs['tasks_specs']:
            for action_id in task_specs['action_list']:
                action_times = [max(agent_specs['skills'][action_id]['t'])
                                for agent_specs in team_specs['agents_specs']]
                worst_case_time += max(action_times)

        return worst_case_time
