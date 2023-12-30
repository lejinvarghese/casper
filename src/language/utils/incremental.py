import os
from datetime import datetime

def get_recently_updated_files(directory):
    directory = os.path.join(os.getcwd(), directory)
    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            # Get the modification time in seconds since the epoch
            modification_unixtime = os.path.getmtime(filepath)
            modification_time = datetime.fromtimestamp(modification_unixtime)
    
    files.sort(key=lambda x: x[1], reverse=True)
    return files

# Example usage:
directory_path = 'src/language/data/.pdfs/'
recent_files = get_recently_updated_files(directory_path)
for file, modification_time in recent_files:
    print(f"File: {file}, Last Modified: {modification_time}")
