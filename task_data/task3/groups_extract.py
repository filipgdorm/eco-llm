
import os
import re
from dotenv import load_dotenv
import requests
import pandas as pd
import json
from tqdm import tqdm

load_dotenv()
api_key=os.environ.get("IUCN_API_KEY")

#get groups:
def get_groups(api_key):
    url = f"https://apiv3.iucnredlist.org/api/v3/comp-group/list?token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def get_species_in_group(group, api_key):
    url = f"https://apiv3.iucnredlist.org/api/v3/comp-group/getspecies/{group}?token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
groups = get_groups(api_key)["result"]

output_json = {}
for group in tqdm(groups):
    species = get_species_in_group(group["group_name"], api_key)["result"]
    output_json[group["group_name"]] = species

    with open('common_groups.json', 'w') as outfile:
        json.dump(output_json, outfile, indent=4)
