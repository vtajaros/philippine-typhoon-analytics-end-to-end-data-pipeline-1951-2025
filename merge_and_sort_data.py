
import csv
import os

main_file = "x:\\Programming\\Python\\Japan Typhoons\\ph_typhoon_names_1963_1999.csv"
missing_file = "x:\\Programming\\Python\\Japan Typhoons\\missing_typhoon_names.csv"
backup_file = "x:\\Programming\\Python\\Japan Typhoons\\ph_typhoon_names_1963_1999.bak"

def read_csv(file_path):
    with open(file_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        data = list(reader)
    return header, data

# Read files
header_main, data_main = read_csv(main_file)
header_missing, data_missing = read_csv(missing_file)

# Combine
# Check if 1965-1969, 1971-1983 already exist in main to avoid duplicates if run multiple times
existing_years = set(row[0] for row in data_main)
new_data = []

# Assuming the main file has gaps, we just add everything from missing file 
# that isn't functionally a duplicate (same year/name).
# Actually, the simplest approach for this specific task is to merge all and sort, 
# relying on the fact that I know the main file has gaps.
# However, to be safe, I'll filter out the years I know I'm adding if they somehow exist, 
# or just trust the sort.
# Let's just combine all rows.

all_data = data_main + data_missing

# Sort by Year (column 0), then International Name (column 1)
# Year should be integer for correct sorting
all_data.sort(key=lambda x: (int(x[0]), x[1]))

# Create backup
if os.path.exists(main_file):
    import shutil
    shutil.copy2(main_file, backup_file)
    print(f"Backup created at {backup_file}")

# Write back
with open(main_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header_main)
    writer.writerows(all_data)

print(f"Successfully merged. Total rows: {len(all_data)}")
