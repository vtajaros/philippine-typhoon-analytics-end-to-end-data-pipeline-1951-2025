import csv

input_file = 'x:\\Programming\\Python\\Japan Typhoons\\ph_typhoon_names_2000_2025.csv'
output_file = 'x:\\Programming\\Python\\Japan Typhoons\\ph_typhoon_names_2000_2025_fixed.csv'

updated_rows = []
with open(input_file, 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    updated_rows.append(header)
    for row in reader:
        # Check for Mindulle 2021
        if row[0] == '2021' and row[1] == 'Mindulle':
            print("Found Mindulle (2021). Removing row.")
            continue
        updated_rows.append(row)

with open(input_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(updated_rows)

print("Updated file.")
