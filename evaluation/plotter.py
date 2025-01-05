import pandas as pd
import matplotlib.pyplot as plt

executor_monitoring_path = 'kmeans-ellis-executor-monitoring.csv'
application_runs_path = 'kmeans-ellis.csv'

executor_data = pd.read_csv(executor_monitoring_path)
application_data = pd.read_csv(application_runs_path)

# Convert times to datetime objects
executor_data['Time'] = pd.to_datetime(executor_data['Time'])
application_data['Start Time Full'] = pd.to_datetime('2025-01-05 ' + application_data['Start Time'])
application_data['End Time Full'] = pd.to_datetime('2025-01-05 ' + application_data['End Time'])

# Add Application Index to the application data
application_data['Application Index'] = application_data.index + 1

# Assign Phases and filter out training runs
# Training runs: 1-10
# 3-minute target: 11-15
# 8-minute target: 16-20
# 5-minute target: 21-25
application_data['Phase'] = pd.cut(
    application_data['Application Index'],
    bins=[0, 10, 15, 20, 25],
    labels=['Training', '3-min target', '9-min target', '5-min target']
)

# Filter out training runs
application_data = application_data[application_data['Phase'] != 'Training']

# Step 1: Normalize Time for Non-Training Runs
normalized_data = []
for _, app in application_data.iterrows():
    app_executor_data = executor_data[
        (executor_data['Time'] >= app['Start Time Full']) &
        (executor_data['Time'] <= app['End Time Full'])
        ].copy()
    app_executor_data['Relative Time'] = (app_executor_data['Time'] - app['Start Time Full']).dt.total_seconds()
    app_executor_data['Application Index'] = app['Application Index']
    normalized_data.append(app_executor_data)

# Combine all normalized data
normalized_data = pd.concat(normalized_data, ignore_index=True)

# Merge phase info into normalized data
normalized_data = normalized_data.merge(
    application_data[['Application Index', 'Phase']],
    how='left',
    on='Application Index'
)

# Step 2: Plotting
# Set color mapping for phases
phase_colors = {
    '3-min target': 'green',
    '9-min target': 'orange',
    '5-min target': 'red'
}

# Create the plot
plt.figure(figsize=(16, 8))

for phase, color in phase_colors.items():
    phase_data = normalized_data[normalized_data['Phase'] == phase]
    for app_index in phase_data['Application Index'].unique():
        app_data = phase_data[phase_data['Application Index'] == app_index]
        plt.plot(
            app_data['Relative Time'] / 60,  # Convert seconds to minutes
            app_data['Executor Count'],
            color=color,
            alpha=0.7
        )

# Add runtime targets as vertical lines
runtime_targets = [3, 9, 5]  # in minutes
target_labels = ['3-min', '9-min', '5-min']
colors = ['green', 'orange', 'red']

for target, label, color in zip(runtime_targets, target_labels, colors):
    plt.axvline(
        x=target, color=color, linestyle='--', alpha=0.8, label=f'{label} (Target)'
    )

# Add runtime targets as horizontal dashed lines
plt.axhline(y=0, color='black', linestyle='--', alpha=0.5, label="Executor Count = 0")

# Labels and legend
plt.xlabel('Application Runtime in Minutes', fontsize=12)
plt.ylabel('Executor Count', fontsize=12)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

handles = [plt.Line2D([0], [0], color=color, lw=3, label=label) for label, color in phase_colors.items()]
plt.legend(handles=handles, title='Execution Phase', fontsize=12, title_fontsize=14, loc='upper right')

plt.grid(alpha=0.3)

# Show the plot
plt.tight_layout()
plt.savefig("executor_count_plot.svg", format="svg")
