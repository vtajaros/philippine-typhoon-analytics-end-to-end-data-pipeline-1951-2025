import re
import csv
import os

def parse_wiki_data(input_file, output_file):
    data = []
    current_year = None
    
    # Regex to find year headers like "## 1963"
    year_re = re.compile(r'^##\s+(\d{4})')
    
    # Regex to parse the line content
    # Pattern 1: Text with parens like "Type Name (PagasaName)"
    # It might be inside [] or just text.
    # We want to catch: "...: [Type IntName (PagName)](...)" or "...: Type IntName (PagName)"
    # Let's clean the line first by removing date preamble "• Month Day-Day, Year: "
    # But wait, looking at the file:
    # • June 9–10, 1963: [Tropical Storm Rose (Bebeng)](...)
    # We can split by ": "
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for year
        m_year = year_re.match(line)
        if m_year:
            current_year = m_year.group(1)
            continue
            
        if line.startswith('•'):
            if ':' in line:
                parts = line.split(':', 1)
                content = parts[1].strip()
            else:
                # Fallback if no colon (unlikely based on format)
                content = line[1:].strip()
                
            # Remove markdown link syntax to just get the text part, but keep URL if needed?
            # actually, sometimes the text is "Type Name (PagasaName)"
            # sometimes "Type Name" and URL has "(PagasaName)"
            
            # Let's simpler approach: extract all text from line stripping [] and ()
            # Better: Look for pattern `Name (Name)`
            
            # Regex for "Type Name (PagasaName)"
            # We assume the one in parens is PAGASA.
            # examples: 
            # Typhoon Trix (Diding)
            # Tropical Storm Rose (Bebeng)
            # Tropical Depression Oyang -> No parens.
            
            # Remove link artifacts
            # [Text](Url) -> Text (and maybe we check Url)
            
            # Check for Link
            link_match = re.search(r'\[(.*?)\]\((.*?)\)', content)
            
            int_name = "N/A"
            pagasa_name = "N/A"
            
            if link_match:
                text_part = link_match.group(1)
                url_part = link_match.group(2)
                
                # Check text for Parens
                paren_match = re.search(r'([A-Za-z0-9\-\'\s]+)\s+\((.*?)\)', text_part)
                if paren_match:
                    # found "Int (Pagasa)" in text
                    # e.g. "Tropical Storm Rose (Bebeng)"
                    full_int = paren_match.group(1).strip() # "Tropical Storm Rose"
                     # extract just the Name
                    int_name = full_int.split()[-1] # "Rose"
                    if "Depression" in full_int and len(int_name) <= 3 and int_name[-1] == 'W':
                        # "Tropical Depression 06W"
                         int_name = "N/A" # Or keep 06W? Usually PAGASA datasets behave differently. User asked for "International Name". 06W is JTWC. JMA might be unnamed. Let's use it if available.
                         int_name = full_int.split()[-1]
                    
                    pagasa_name = paren_match.group(2).strip()
                else:
                    # No parens in text. e.g. "Tropical Depression Oyang"
                    # Check URL for parens?
                    # Url: ...#Tropical_Storm_Dom_(Oyang)
                    url_paren = re.search(r'\((.*?)\)', url_part)
                    if url_paren:
                         # Found (Oyang) in URL
                         pagasa_name = url_paren.group(1).replace('_', ' ').strip()
                         # The text part likely contains the Int Name or Pagasa Name?
                         # "Tropical Depression Oyang" -> Oyang is Pagasa.
                         # If Text is "Type Oyang", and Url has "Type Dom (Oyang)", then Int is Dom.
                         # Parsing text_part: "Tropical Depression Oyang" -> Name Oyang.
                         # If Oyang == Pagasa, then Int name is hidden or is N/A.
                         # URL might help: "Tropical_Storm_Dom_(Oyang)"
                         # Extract Dom.
                         # regex for URL fragment
                         frag = url_part.split('#')[-1]
                         # Remove (Pagasa)
                         frag_no_pag = frag.replace('(' + pagasa_name + ')', '').replace('_', ' ').strip()
                         # frag_no_pag: "Tropical Storm Dom"
                         int_name = frag_no_pag.split()[-1]
                    else:
                        # No parens in URL either.
                        # e.g. [Typhoon Ike] -> Name Ike.
                        # If no PAG listed?
                        # Maybe formatting is `Type Int (Pag)` outside brackets?
                        # But loop checks `content`.
                        # Let's check if content has parens outside link.
                        pass

            if pagasa_name == "N/A":
                 # Try finding parens in the whole content line (ignoring link brackets if possible, or just naively)
                 # naive:
                 m = re.search(r'\(([A-Za-z]+)\)', content)
                 if m:
                     if m.group(1) not in ["edit", "citation"]: # filter wiki noise if any
                         pagasa_name = m.group(1)
            
            if int_name == "N/A":
                # Try to guess Int Name from text before Parens
                # "Typhoon Trix (Diding)"
                # Remove (Diding) -> Typhoon Trix
                # Split -> Trix
                before_paren = content.split('(')[0]
                # Remove [ ] links
                clean_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', before_paren)
                clean_text = clean_text.replace('[', '').replace(']', '')
                tokens = clean_text.strip().split()
                if tokens:
                     # heuristic: last token is name
                     candidate = tokens[-1]
                     if candidate not in ["Typhoon", "Storm", "Depression", "Super", "Severe"]:
                         int_name = candidate

            # Cleanup
            if int_name == "Depression": int_name = "N/A" # Error handling
            
            # Special logic for "Unnamed"
            if "unnamed" in content.lower():
                int_name = "N/A"
            
            if current_year and pagasa_name != "N/A":
                 data.append([current_year, int_name, pagasa_name])

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Year', 'International Name', 'PAGASA Name'])
        writer.writerows(data)
    
    print(f"Extracted {len(data)} entries.")

if __name__ == "__main__":
    parse_wiki_data('x:\\Programming\\Python\\Japan Typhoons\\raw_wiki_1963_1999.txt', 'x:\\Programming\\Python\\Japan Typhoons\\ph_typhoon_names_1963_1999.csv')
