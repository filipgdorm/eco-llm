import requests
import json
from tqdm import tqdm
import time
from requests.exceptions import ConnectionError, HTTPError

def get_taxon_info(taxon_id, retries=3, delay=2, backoff=2):
    url = f"https://api.inaturalist.org/v1/taxa/{taxon_id}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
            
            data = response.json()
            if data['results']:
                taxon = data['results'][0]
                scientific_name = taxon.get('name')
                common_name = taxon.get('preferred_common_name')
                class_name = taxon.get('iconic_taxon_name')
                return scientific_name, common_name, class_name
            else:
                # If no results, return None
                return None, None, None
        
        except (ConnectionError, HTTPError) as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(delay)
            delay *= backoff  # Exponential backoff
    
    # After retries, return None if still failing
    return None, None, None

# Example usage
with open("gt_data/iucn_res_5.json", 'r') as f:
    data = json.load(f)
taxon_ids = data['taxa_presence'].keys()
species_names = {}

# Track the number of failures
failures = 0

# Fetch species names with progress bar
for i, taxon_id in tqdm(enumerate(taxon_ids), total=len(taxon_ids)):
    scientific_name, common_name, class_name = get_taxon_info(taxon_id)
    
    if scientific_name:
        species_names[taxon_id] = {
            "scientific_name": scientific_name,
            "common_name": common_name,
            "class_name": class_name
        }
    else:
        failures += 1

# Print the number of failures
print(f"Failed to retrieve data for {failures} species.")

# Define the output JSON file path
output_file_path = 'meta_data/iucn_species_names.json'
# Save the species names to a JSON file
with open(output_file_path, 'w') as json_file:
    json.dump(species_names, json_file, indent=2)
