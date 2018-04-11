
def get_scenario():

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
        5001: 'Release salad',
        5002: 'Release olive oil bottle',
        5003: 'Release mixing tool',
        6001: 'Mix salad',
    }

    behavior_specs = {

        'id': 0,
        'name': 'Make a Salad!',
        'tasks_specs': [
            {'id': 101, 'name': 'Place salad on countertop', 'action_list': [1001, 2001, 1002, 3001],
             'constraints': {}},
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
        'name': 'CookingBots',
        'agents_specs': [

            {
                'id': 0,
                'name': 'Alice',
                'skills': {
                    1001: {'t': (21, 32), 'r': 9},
                    1002: {'t': (21, 32), 'r': 9},
                    2001: {'t': (4, 9), 'r': 9},
                    2002: {'t': (6, 9), 'r': 9},
                    2003: {'t': (4, 8), 'r': 9},
                    2004: {'t': (3, 8), 'r': 9},
                    3001: {'t': (3, 7), 'r': 9},
                    3002: {'t': (4, 7), 'r': 9},
                    3003: {'t': (3, 5), 'r': 9},
                    3004: {'t': (4, 6), 'r': 9},
                    4001: {'t': (7, 10), 'r': 9},
                    4002: {'t': (5, 8), 'r': 9},
                    5001: {'t': (2, 4), 'r': 9},
                    5002: {'t': (3, 5), 'r': 9},
                    5003: {'t': (3, 5), 'r': 9},
                    6001: {'t': (5, 11), 'r': 9},
                }
            },

            {
                'id': 1,
                'name': 'Bob',
                'skills': {
                    1001: {'t': (22, 38), 'r': 9},
                    1002: {'t': (22, 38), 'r': 9},
                    2001: {'t': (6, 10), 'r': 7},
                    2002: {'t': (7, 10), 'r': 5},
                    2003: {'t': (7, 10), 'r': 7},
                    2004: {'t': (5, 9), 'r': 7},
                    3001: {'t': (4, 8), 'r': 7},
                    3002: {'t': (5, 7), 'r': 7},
                    3003: {'t': (3, 6), 'r': 7},
                    3004: {'t': (3, 8), 'r': 5},
                    4001: {'t': (7, 12), 'r': 7},
                    4002: {'t': (5, 7), 'r': 9},
                    5001: {'t': (3, 6), 'r': 9},
                    5002: {'t': (3, 6), 'r': 9},
                    5003: {'t': (3, 8), 'r': 9},
                    6001: {'t': (6, 14), 'r': 7},
                }
            }
        ]
    }

    return actions_names, behavior_specs, team_specs
