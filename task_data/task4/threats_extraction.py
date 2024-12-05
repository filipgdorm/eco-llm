import os
import re
import json
from dotenv import load_dotenv
import requests

load_dotenv()
api_key=os.environ.get("IUCN_API_KEY")

def clean_string(input_string):
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', input_string)
    
    # Replace HTML entities with their respective characters
    clean_text = clean_text.replace('&#160;', ' ')

    # Remove extra whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    return clean_text

def get_threats(species_id, api_key):
    url = f'https://apiv3.iucnredlist.org/api/v3/threats/species/id/{species_id}?token={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_description(species_id, api_key):
    url = f'https://apiv3.iucnredlist.org/api/v3/species/narrative/id/{species_id}?token={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def get_history(species_id, api_key):
    url = f'https://apiv3.iucnredlist.org/api/v3/species/history/id/{species_id}?token={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
species_data = {}

#choose species names 
with open("../../data/meta_data/inat_iucn_conversion.json", "r") as file:
    inat_iucn_id_pairs = json.load(file)
 
for inat_id, iucn_id in inat_iucn_id_pairs.items():
    
    threats_data = get_threats(iucn_id, api_key)
    description = get_description(iucn_id, api_key)
    history = get_history(iucn_id, api_key)

    species_info = {}

    # Check if all data is available
    if (len(threats_data["result"])>0 and description["result"][0].get("threats")):
        
        # Populate the species_info dictionary
        species_info = history["result"][0]  # Start with history data
        species_info["iucn_id"] = str(iucn_id)
        species_info["threats"] = threats_data["result"]
        
        # Clean and add threats description
        species_info["threats_description"] = clean_string(description["result"][0].get("threats", "No description available"))
        
        # Add to species_data only if all data is present
        species_data[str(inat_id)] = species_info
    else:
        print(f"Skipping {inat_id} due to missing data.")


# Save the species names to a JSON file
output_file_path = 'iucn_threats.json'
with open(output_file_path, 'w') as json_file:
    json.dump(species_data, json_file, indent=2)
