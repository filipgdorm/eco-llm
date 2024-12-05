import json

import requests
import os

from dotenv import load_dotenv


load_dotenv()
api_key=os.environ.get("IUCN_API_KEY")

#get countries:
def get_all_countries(api_key):
    url = f"https://apiv3.iucnredlist.org/api/v3/country/list?token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
#get countries:
def get_species_in_country(isocode, api_key):
    url = f"https://apiv3.iucnredlist.org/api/v3/country/getspecies/{isocode}?token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

countries = get_all_countries(api_key)["results"]
country_data = {}
for entry in countries:
    isocode = entry["isocode"]
    country = entry["country"]

    species = get_species_in_country(isocode, api_key)["result"]

    countries_info = {}
    countries_info["full_name"] = country
    countries_info["species"] = species

    country_data[isocode] = countries_info

# Write the data to a JSON file
with open('countries_w_species.json', 'w') as f:
    json.dump(country_data, f, indent=2)
