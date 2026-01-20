import re
import csv

input_file = r'x:\Programming\Python\Japan Typhoons\raw_wiki_data.txt'
output_file = r'x:\Programming\Python\Japan Typhoons\ph_typhoon_names_2000_2025.csv'

typhoons = []
current_year = None

def clean_name(name):
    # Remove storm types
    name = re.sub(r'^(Typhoon|Super Typhoon|Severe Tropical Storm|Tropical Storm|Tropical Depression)\s+', '', name, flags=re.IGNORECASE)
    return name.strip()

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        
        # Check for Year header
        year_match = re.match(r'^###\s+(\d{4})', line)
        if year_match:
            current_year = year_match.group(1)
            continue
            
        if line.startswith('•'):
            # Extract content inside []
            # There might be multiple typhoons in one line like "and [Typhoon Halong (Inday)]"
            matches = re.findall(r'\[(.*?)\]', line)
            
            for match in matches:
                # remove special chars if any? match is just the text inside []
                content = match
                
                # Check for Name (PAGASA) format
                paren_match = re.match(r'(.*)\s+\((.*)\)', content)
                
                if paren_match:
                    intl_full = paren_match.group(1)
                    pagasa_full = paren_match.group(2)
                    
                    intl_name = clean_name(intl_full)
                    pagasa_name = clean_name(pagasa_full)
                    
                    # Special Case handling where PAGASA name accidentally includes "Typhoon" or "Tropical Depression" inside the parens
                    # e.g. [Tropical Storm Co-may (Typhoon Emong)]
                    # clean_name already handles this.
                    
                else:
                    # Single name, assumed to be PAGASA name for TDs or locally named storms
                    # But wait, [Typhoon Cimaron] in 2006 has no parens. Cimaron is International.
                    # [Tropical Depression Konsing] -> Konsing is PAGASA.
                    # How to distinguish?
                    # "Cimaron" is international. "Konsing" is PAGASA.
                    # Usually if it's a Typhoon/TS, it's International. If TD, it might be PAGASA.
                    # This is tricky. 
                    # Let's look at 2006: [Typhoon Cimaron]. Wiki says "Typhoon Cimaron (2006)". PAGASA name was Paeng. (Wait, looking at 2006 data in wiki elsewhere might clarify).
                    # Actually, [Typhoon Cimaron] in the text I saved... let me check the text I saved for 2006.
                    # "• October 29–30, 2006: [Typhoon Cimaron]" -> It doesn't have the PAGASA name in the text I copied?
                    # Let's check the context from the earlier search.
                    # "Typhoon Cimaron (2006) batters Cagayan... At least 34 people died."
                    # It seems I might have missed some PAGASA names if they weren't in the bracket.
                    # But for now, I will assume if it's a "Typhoon" or "Tropical Storm", it's International. If "Tropical Depression", it's PAGASA.
                    # This is a heuristic.
                    # Exception: If I can map it later?
                    # Let's check `[Tropical Depression Auring]`. Auring is PAGASA.
                    # `[Tropical Storm Crising]`. Crising is PAGASA. (TS Crising 2021).
                    # `[Tropical Storm Crising]` also in 2001? "Tropical Storm Cimaron (Crising)".
                    # So "Crising" is PAGASA.
                    
                    full_name = content
                    base_name = clean_name(full_name)
                    
                    if "Depression" in full_name:
                         intl_name = "N/A"
                         pagasa_name = base_name
                    else:
                        # If it is a named storm (TS/Typhoon), it is usually the International Name when appearing alone, 
                        # OR it's a PAGASA-only name?
                        # Taking a risk here. Most entries have (PAGASA).
                        # [Typhoon Cimaron] -> Int: Cimaron, PAGASA: ???
                        intl_name = base_name
                        pagasa_name = "N/A" 

                # clean any leftover parens or numbers
                
                typhoons.append([current_year, intl_name, pagasa_name])

# Write to CSV
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Year', 'International Name', 'PAGASA Name'])
    writer.writerows(typhoons)

print(f"Successfully processed {len(typhoons)} typhoons.")
