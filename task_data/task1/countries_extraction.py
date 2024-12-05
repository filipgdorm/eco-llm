import json
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv
import requests
import os

load_dotenv()
api_key=os.environ.get("IUCN_API_KEY")

def get_countries(species_id, api_key):
    url = f"https://apiv3.iucnredlist.org/api/v3/species/countries/id/{species_id}?token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def get_description(species_id, api_key):
    url = f'https://apiv3.iucnredlist.org/api/v3/species/id/{species_id}?token={api_key}'
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
    species_info = {}
    countries_info = get_countries(iucn_id, api_key)
    description = get_description(iucn_id, api_key)

    species_info["iucn_id"] = str(iucn_id)
    # Check if the description list is empty
    if len(description["result"])>0:
        species_info["redlist_category"] = description["result"][0]["category"]
    else:
        species_info["redlist_category"] = None  # Set to None if the list is empty    
    species_info["countries"] = countries_info["result"]

    species_data[str(inat_id)] = species_info

# Write the data to a JSON file
with open('iucn_species_countries.json', 'w') as f:
    json.dump(species_data, f, indent=2)
