import os
import pandas as pd
import random
from datetime import datetime, timedelta

# Path to the folder containing the CSV files
folder_path = 'evaluation/test'
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Define weekly increment and duration (52 weeks)
weekly_increment = timedelta(weeks=1)
num_weeks = 52
for file_name in csv_files:
    file_path = os.path.join(folder_path, file_name)
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Get the last date in the first row, which represents weekly intervals
    last_date_str = df.columns[-1]
    last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
    
    # Generate new weekly dates for the next 52 weeks
    new_dates = [(last_date + weekly_increment * i).strftime('%Y-%m-%d') for i in range(1, num_weeks + 1)]
    
    # Add new columns for each new date
    for new_date in new_dates:
        df[new_date] = None  # Initialize new columns with None values
    
    # Fill each new column with values by adding a random number between 0 and 10
    for row_idx in range(len(df)):
        if row_idx % 3 == 0:  # Skip every 3rd row
            continue
        
        last_value = df.iloc[row_idx, -num_weeks - 1]
        
        # For each new date column, add a random number between 0 and 10 to the last known value
        for i, new_date in enumerate(new_dates):
            random_increment = random.randint(0, 10)
            df.loc[row_idx, new_date] = last_value + random_increment
            last_value = df.loc[row_idx, new_date]  # Update last_value to use the current week's value for the next
            
    # Overwrite the original file with the modified DataFrame
    df.to_csv(file_path, index=False)
    print(f"Updated file: {file_name}")