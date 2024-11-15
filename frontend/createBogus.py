import os
import pandas as pd

# Define the folder path containing the CSV files
folder_path = 'evaluation/US-COVID/state_death_eval'

# Get all CSV files in the folder
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv') and f.startswith('mae')]

# Iterate through each CSV file
for file_name in csv_files:
    # Define the full file path
    file_path = os.path.join(folder_path, file_name)
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Modify the first column (forecast methods) and the rest of the columns
    # Increase performance values by 10 (assuming the performance data starts from the second column)
    df.iloc[:, 1:] = df.iloc[:, 1:] + 10  # Increment performance values by 10
    
    # Replace 'mae' with 'bogus' in the file name
    new_file_name = file_name.replace('mae', 'bogus', 1)  # Only replace the first occurrence of 'mae'
    new_file_path = os.path.join(folder_path, new_file_name)
    
    # Write the modified DataFrame to the new CSV file
    df.to_csv(new_file_path, index=False)
    
    print(f"Processed file: {new_file_name}")
