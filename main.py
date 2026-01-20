import pandas as pd
import os
import sys

# --- CONFIGURATION ---
INPUT_FILE = 'bst_all.txt'
MAPPING_FILE = 'pagasa_mapping_all.csv'
OUTPUT_FILE = 'ph_typhoon_data_v2.csv'

# PAR POLYGON VERTICES (Longitude, Latitude)
# (25°N, 120°E), (25°N, 135°E), (5°N, 135°E), (5°N, 115°E), (15°N, 115°E), (21°N, 120°E)
PAR_VERTICES = [
    (120.0, 25.0),
    (135.0, 25.0),
    (135.0, 5.0),
    (115.0, 5.0),
    (115.0, 15.0),
    (120.0, 21.0)
    # Implicitly closes back to (120, 25)
]

def estimate_wind_from_pressure(pressure):
    """
    Estimates 1-min sustained wind speed (kt) from central pressure (hPa)
    using the Atkinson & Holliday (1977) relationship for the NW Pacific.
    V = 6.7 * (1010 - Pc) ^ 0.644
    Note: JMA uses 10-min sustained; this approximation is close enough for
    categorical classification of older storms where data is sparse.
    """
    if pressure is None or pressure >= 1010:
        return 0
    try:
        return 6.7 * ((1010 - pressure) ** 0.644)
    except Exception:
        return 0

def get_classification(grade_str, wind_kt_str, pressure_str=None):
    """
    Classifies the storm based on PAGASA 2022 standards using Grade and WindSpeed.
    Falls back to Pressure-based estimation for historical data (Pre-1977).
    """
    try:
        grade = int(grade_str) if grade_str and grade_str.strip() else -1
    except ValueError:
        grade = -1
        
    wind = None
    try:
        if wind_kt_str and wind_kt_str.strip():
            wind = float(wind_kt_str)
    except ValueError:
        pass
        
    pressure = None
    try:
        if pressure_str and pressure_str.strip():
            pressure = float(pressure_str)
    except ValueError:
        pass

    # 1. Special Grades
    if grade == 6:
        return "Extra-tropical Cyclone"
        
    # 2. Wind Speed Logic (Real Data)
    if wind is not None:
        if wind < 34:
            return "Tropical Depression"
        elif 34 <= wind <= 47:
            return "Tropical Storm"
        elif 48 <= wind <= 63:
            return "Severe Tropical Storm"
        elif 64 <= wind <= 99:
            return "Typhoon"
        elif wind >= 100:
            return "Super Typhoon"
            
    # 3. Fallback: Estimate Wind from Pressure (Atkinson & Holliday)
    # Applied if wind is missing AND we have a valid pressure
    # Especially for Grade 9 (TS+) or Grade 2/7/etc in old data
    if wind is None and pressure is not None:
        est_wind = estimate_wind_from_pressure(pressure)
        # Apply the same thresholds logic
        if est_wind < 34:
             # If Grade is 9 (TS+), force at least TS?
             # Standard A&H might under-estimate weak storms near 1000hPa.
             # However, let's stick to the physical relation.
             # But if Grade == 9, it implies >= 34kt (TS).
             if grade == 9: 
                 return "Tropical Storm"
             return "Tropical Depression"
        elif 34 <= est_wind <= 47:
            return "Tropical Storm"
        elif 48 <= est_wind <= 63:
            return "Severe Tropical Storm"
        elif 64 <= est_wind <= 99:
            return "Typhoon"
        elif est_wind >= 100:
            return "Super Typhoon"

    # 4. Fallback based on Grade (if no wind AND no pressure, or edges)
    if grade == 2:
        return "Tropical Depression"
    elif grade == 3:
        return "Tropical Storm"
    elif grade == 4:
        return "Severe Tropical Storm"
    elif grade == 5:
        return "Typhoon"
    # Grade 9 without pressure/wind cannot be specifically classified beyond "TS or higher"
    # But often treated as generic TS if we must pick.
    elif grade == 9:
        return "Tropical Storm" # Minimal assumption
        
    return ""

def is_in_par(lat, lon):
    """
    Ray-casting algorithm to check if a point is inside the PAR polygon.
    """
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return False
        
    inside = False
    j = len(PAR_VERTICES) - 1
    for i in range(len(PAR_VERTICES)):
        xi, yi = PAR_VERTICES[i]
        xj, yj = PAR_VERTICES[j]
        
        # Check intersect logic
        intersect = ((yi > lat) != (yj > lat)) and \
            (lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-10) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside

def load_mappings():
    """
    Loads mapping from CSV and applies manual overrides.
    Returns a dict: (Year, Name_Upper) -> PAGASA_Name
    """
    mapping = {}
    
    # 1. Load from CSV if exists
    if os.path.exists(MAPPING_FILE):
        try:
            df_map = pd.read_csv(MAPPING_FILE)
            for _, row in df_map.iterrows():
                try:
                    yr = int(row['Year'])
                    intl = str(row['International Name']).strip().upper()
                    pagasa = str(row['PAGASA Name']).strip()
                    if intl and intl != 'NAN' and intl != 'N/A':
                        mapping[(yr, intl)] = pagasa
                except (ValueError, IndexError):
                    continue
            print(f"Loaded {len(mapping)} mappings from CSV.")
        except Exception as e:
            print(f"Warning: Could not load {MAPPING_FILE}: {e}")
    
    # 2. Apply Manual Overrides
    # format: (Year, International_Name) -> PAGASA_Name
    manual_overrides = {
        (1979, 'TIP'): 'WARLING',
        (1975, 'JUNE'): 'ROSING',
        (1973, 'NORA'): 'LUING',
        (1978, 'RITA'): 'KADING',
        (1984, 'VANESSA'): 'NITANG',
        (1966, 'KIT'): 'EMANG',
        (1983, 'FORREST'): 'ISING',
        (1971, 'IRMA'): 'INING',
        (1990, 'FLO'): 'BIDANG',
        (1981, 'ELSIE'): 'TASING',
        (2015, 'SOUDELOR'): 'HANNA'
    }
    
    mapping.update(manual_overrides)
    print(f"Total mappings after overrides: {len(mapping)}")
    return mapping

def parse_jma_data(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return None

    current_id = None
    current_name = None
    
    # Store storm-level flags
    # We need a pass to determine if a storm ID EVER entered PAR
    # To avoid two passes, we'll store rows by ID, then process.
    storms = {} # ID -> list of rows
    
    print("Parsing JMA data...")
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('66666'):
                current_id = line[6:10].strip()
                current_name = line[30:50].strip()
                if not current_name:
                    current_name = "UNNAMED"
                
                # JMA IDs repeat after decades, but usually distinct in file sequence.
                # To distinguish duplicates like Haiyan 2001 vs 2013, we rely on unique IDs in standard JMA files
                # or we key by (ID, Year). However, JMA usually uses unique YYNN format.
                # Let's trust current_id is unique enough for file scope.
                
                if current_id not in storms:
                    storms[current_id] = {'rows': [], 'name': current_name, 'entered_par': False}
                continue
            
            # Data Line
            try:
                date_str = line[0:8].strip()      # YYMMDDHH
                grade = line[13:14].strip()
                lat_raw = line[15:18].strip()
                long_raw = line[19:23].strip()
                pressure = line[24:28].strip()
                wind = line[33:36].strip()
                
                lat = float(lat_raw) / 10.0 if lat_raw else None
                long = float(long_raw) / 10.0 if long_raw else None
                
                # Year Handling
                yy = int(date_str[:2])
                year = 1900 + yy if yy > 50 else 2000 + yy
                full_ts = f"{year}{date_str[2:]}"
                
                # Check PAR
                in_par = False
                if lat is not None and long is not None:
                    in_par = is_in_par(lat, long)
                
                row = {
                    'StormID': current_id,
                    'StormName': current_name,
                    'Timestamp': full_ts,
                    'Year': year,
                    'Latitude': lat,
                    'Longitude': long,
                    'Grade': grade,
                    'Pressure_hPa': pressure,
                    'WindSpeed_kt': wind,
                    'In_PAR': in_par
                }
                
                storms[current_id]['rows'].append(row)
                if in_par:
                    storms[current_id]['entered_par'] = True
                    
            except ValueError:
                continue
                
    return storms

def process_and_export(storms, mappings):
    final_rows = []
    
    print("Processing names and geofencing...")
    for storm_id, data in storms.items():
        entered_par = data['entered_par']
        rows = data['rows']
        name = data['name']
        
        if not rows:
            continue
            
        first_year = rows[0]['Year']
        lookup_name = name.upper()
        
        pagasa_name = ""
        
        # Priority 1: Mapping Dict (Year, Name)
        found_name = mappings.get((first_year, lookup_name))
        
        # Priority 2: Historical & Location fallback
        if found_name:
            pagasa_name = found_name
        elif entered_par:
            if first_year < 1963:
                pagasa_name = "PRE-1963"
        else:
            pagasa_name = "OUTSIDE PAR"
            
        has_entered_so_far = False
        for row in rows:
            row['PAGASA_Name'] = pagasa_name
            # Classification
            row['Classification'] = get_classification(row['Grade'], row['WindSpeed_kt'], row['Pressure_hPa'])
            
            # Update In_PAR Logic (Stateful)
            currently_in = row['In_PAR']
            if currently_in:
                has_entered_so_far = True
                row['In_PAR'] = "Inside PAR"
            elif has_entered_so_far:
                row['In_PAR'] = "Exited PAR"
            else:
                row['In_PAR'] = "Outside PAR"
            
            # Create final structure
            final_rows.append(row)
            
    df = pd.DataFrame(final_rows)
    
    # Columns order
    cols = ['StormID', 'StormName', 'PAGASA_Name', 'Classification', 'Timestamp', 'In_PAR', 
            'Latitude', 'Longitude', 'Pressure_hPa', 'WindSpeed_kt', 'Grade', 'Year']
    
    # Ensure all exist
    existing_cols = [c for c in cols if c in df.columns]
    df = df[existing_cols]
    
    try:
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Success! Saved {len(df)} rows to {OUTPUT_FILE}")
    except PermissionError:
        fallback_file = "ph_typhoon_data_v4.csv"
        df.to_csv(fallback_file, index=False)
        print(f"Notice: {OUTPUT_FILE} and v3 were locked. Saved to {fallback_file} instead.")
    
    # Validation stats
    par_entries = df[df['In_PAR'] == "Inside PAR"]
    print(f"Rows inside PAR: {len(par_entries)}")
    
    pre63 = df[df['PAGASA_Name'] == 'PRE-1963']
    print(f"Historical (Pre-1963) PAR storms identified: {pre63['StormID'].nunique()}")
    
    mapped = df[ (df['PAGASA_Name'] != '') & (df['PAGASA_Name'].notna()) ]
    print(f"Total rows with PAGASA names: {len(mapped)}")

def main():
    # Setup paths relative to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    mappings = load_mappings()
    storms = parse_jma_data(INPUT_FILE)
    
    if storms:
        process_and_export(storms, mappings)

if __name__ == "__main__":
    main()
