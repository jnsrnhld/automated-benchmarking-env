import pandas as pd
from datetime import datetime, timedelta

# Load the CSV file
file_path = 'your_file_path_here.csv'
data = pd.read_csv(file_path)

# Function to calculate start time based on end time and duration
def calculate_start_time(row):
    end_time = datetime.strptime(row['Time'], '%H:%M:%S')
    duration = timedelta(seconds=row['Duration'])
    start_time = end_time - duration
    return start_time.time()

# Apply the function to the DataFrame
data['Start Time'] = data.apply(calculate_start_time, axis=1)

# Save the updated DataFrame or use it as needed
data.to_csv('output_with_start_times.csv', index=False)
print(data.head())
