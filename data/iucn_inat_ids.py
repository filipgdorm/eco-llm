import requests
import json
import time
from tqdm import tqdm

def fetch_iucn_code(inat_id, retries=10, delay=2):
    sparql_url = "https://query.wikidata.org/sparql"
    query = f"""
    SELECT ?iucncode WHERE {{
        VALUES ?inatcode {{ "{inat_id}" }}
        ?animal wdt:P3151 ?inatcode;
                wdt:P627 ?iucncode.
    }}
    """
    
    headers = {
        "Accept": "application/sparql-results+json"
    }

    for attempt in range(retries):
        try:
            response = requests.get(sparql_url, params={'query': query}, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                results = data['results']['bindings']
                if results:
                    return results[0]['iucncode']['value']
                else:
                    return None
            else:
                print(f"Query failed with status code {response.status_code}. Attempt {attempt + 1} of {retries}.")
                time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Attempt {attempt + 1} of {retries}.")
            time.sleep(delay)
    
    raise Exception(f"Query failed after {retries} attempts for iNaturalist ID {inat_id}")

def process_inat_ids(inat_ids):
    iucn_dict = {}
    for i, inat_id in tqdm(enumerate(inat_ids), total=len(inat_ids)):
        try:
            iucn_code = fetch_iucn_code(inat_id)
            if iucn_code:
                iucn_dict[inat_id] = iucn_code
            else:
                print(f"No IUCN code found for iNaturalist ID {inat_id}")
        except Exception as e:
            print(e)
    return iucn_dict

# Example usage
with open("meta_data/iucn_species_names.json", "r") as file:
    species_names = json.load(file)

inat_ids = species_names.keys()
    
iucn_mapping = process_inat_ids(inat_ids)

print(iucn_mapping)

# Save the species names to a JSON file
output_file_path = 'meta_data/inat_iucn_conversion.json'
with open(output_file_path, 'w') as json_file:
    json.dump(iucn_mapping, json_file, indent=2)


