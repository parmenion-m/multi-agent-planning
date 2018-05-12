
import pandas as pd
import matplotlib.pyplot as plt


# input file for analysis:
csv_filename = 'experiment-1000-custom_5_20'


# ----- Data preparation -----
data = pd.read_csv('reports/%s.csv' % csv_filename)
planners = sorted(list(data['planner'].unique()))
agent_ids = sorted(list(set([int(col.split('_')[1]) for col in data.columns if col.split('_')[0] == 'ag'])))


# ----- Behaviors completed -----
planners_vs_behaviors = data[['planner', 'behavior_status']].groupby(['planner', 'behavior_status']).size()
print('\nPlanners vs Behaviors:\n', planners_vs_behaviors)


# ----- Time spent & Robustness -----
time_spent = pd.DataFrame()
robustness = pd.DataFrame()

for planner in planners:
    time_spent[planner] = data[data['planner'] == planner]['time_spent'].reset_index(drop=True)
    robustness[planner] = data[data['planner'] == planner]['robustness'].reset_index(drop=True)

print('\nTime spent:\n', time_spent.describe())
print('\nRobustness:\n', robustness.describe())


# ----- Team status -----
data['Resting'] = 0
data['Waiting'] = 0
data['Working'] = 0
data['Total time'] = 0

for agent_id in agent_ids:
    data['Resting'] = data['Resting'] + data['ag_%s_rest' % agent_id]
    data['Waiting'] = data['Waiting'] + data['ag_%s_wait' % agent_id]
    data['Working'] = data['Working'] + data['ag_%s_work' % agent_id]
    data['Total time'] = data['Total time'] + data['ag_%s_total' % agent_id]

# columns as phases (rest / wait / work), rows as planners (base / dpv1 / etc.)
team_status_means = data.groupby('planner').sum()[['Resting', 'Waiting', 'Working']]
# team_status_stds = data.groupby('planner').std()[['Resting', 'Waiting', 'Working']]
print('\nTeam status:\n', team_status_means)


# ----- Figures -----
plt.style.use('ggplot')
fig, axes = plt.subplots(nrows=1, ncols=3)

time_spent.plot.box(ax=axes[0], notch=True, showfliers=False, patch_artist=True)
axes[0].set_title('Time spent')
axes[0].tick_params(axis='x', rotation=90)

robustness.plot.box(ax=axes[1], notch=True,  showfliers=False, patch_artist=True)
axes[1].set_title('Robustness')
axes[1].tick_params(axis='x', rotation=90)

team_status_means.plot.bar(ax=axes[2], stacked=True)  # , yerr=team_status_stds)
axes[2].set_title('Team status')
axes[2].set_xlabel('')
axes[2].legend(loc=5)

plt.show()
fig.savefig('reports/%s.png' % csv_filename)
