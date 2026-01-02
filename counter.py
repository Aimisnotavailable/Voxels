import os

def count_lines_in_file(file_path):
    """Count lines in a single file efficiently."""
    try:
        with open(file_path, 'r', errors='ignore') as file:
            return sum(1 for line in file)
    except PermissionError:
        return 0 # Handle unreadable files

def count_lines_in_folder(folder_path):
    """Recursively count lines in all .py files within a folder and subfolders."""
    total_lines = 0
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                total_lines += count_lines_in_file(filepath)
    return total_lines

# Specify the directory you want to analyze ('.' for current directory)
directory_to_scan = '.' 
total_lines_of_code = count_lines_in_folder(directory_to_scan)

print(f"Total lines of Python code in '{directory_to_scan}': {total_lines_of_code}")
