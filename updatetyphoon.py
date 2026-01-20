import pandas as pd
import os

def load_pagasa_mapping(mapping_file):
    mapping = {}
    if not os.path.exists(mapping_file):
        print(f"Warning: Mapping file {mapping_file} not found. Using empty mapping.")
        return mapping
        
    try:
        df_map = pd.read_csv(mapping_file)
        # Ensure we work with strings and handle missing values
        df_map['International Name'] = df_map['International Name'].fillna('').astype(str).str.strip().str.upper()
        df_map['PAGASA Name'] = df_map['PAGASA Name'].fillna('').astype(str).str.strip().str.upper()
        
        for _, row in df_map.iterrows():
            year = int(row['Year'])
            intl_name = row['International Name']
            pagasa_name = row['PAGASA Name']
            
            if intl_name and intl_name != 'N/A':
                mapping[(year, intl_name)] = pagasa_name
                
    except Exception as e:
        print(f"Error loading mapping file: {e}")
        
    return mapping

def parse_and_map_typhoons(file_path):
    # Load PAGASA mappings from CSV
    mapping_csv = os.path.join(os.path.dirname(__file__), 'pagasa_mapping_all.csv')
    mapping = load_pagasa_mapping(mapping_csv)
    
    # Add manual fallback for older typhoons not in CSV or special cases
    manual_mapping = {
        (1991, 'THELMA'): 'URING'
    }
    mapping.update(manual_mapping)

    data_rows = []
    current_name, current_id = None, None

    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('66666'):
                current_id = line[6:10].strip()
                current_name = line[30:50].strip() or "UNNAMED"
                continue
            
            date_str = line[0:8].strip()
            year = int("19" + date_str[:2]) if int(date_str[:2]) > 50 else int("20" + date_str[:2])
            
            # Create the row
            row = {
                'StormID': current_id,
                'StormName': current_name,
                'PAGASA_Name': mapping.get((year, current_name.upper()), ""),
                'Timestamp': f"{year}{date_str[2:]}",
                'Latitude': float(line[15:18]) / 10.0,
                'Longitude': float(line[19:23]) / 10.0,
                'Pressure_hPa': line[24:28].strip()
            }
            data_rows.append(row)
    
    df = pd.DataFrame(data_rows)
    output_file = 'ph_typhoon_data_complete.csv'
    try:
        df.to_csv(output_file, index=False)
        print(f"File successfully created: {output_file}")
    except PermissionError:
        print(f"Error: Could not write to {output_file}. Is it open in Excel?")
        output_file_fallback = 'ph_typhoon_data_complete_v2.csv'
        df.to_csv(output_file_fallback, index=False)
        print(f"Saved to {output_file_fallback} instead.")

parse_and_map_typhoons('bst_all.txt')