import os

# Specify the folder path
folder_path = 'evaluation/US-COVID/state_death_eval'  # Replace with the actual folder path

# Iterate through all files in the folder
for filename in os.listdir(folder_path):
    # Check if the file starts with 'mae'
    if filename.startswith('mae'):
        # Create the new filename by replacing 'mae' with 'bogus'
        new_filename = 'bogus' + filename[3:]
        
        # Construct full file paths
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)
        
        # Rename the file
        os.rename(old_file_path, new_file_path)

        print(f'Renamed: {filename} -> {new_filename}')
