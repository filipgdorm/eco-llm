import os
import re
from dotenv import load_dotenv
import requests
import pandas as pd
import json
from tqdm import tqdm
tqdm.pandas()

load_dotenv()
api_key=os.environ.get("IUCN_API_KEY")

df = pd.read_json("countries_w_species.json",orient='index')
df_output = df.explode('species').reset_index()
df_normalized = pd.json_normalize(df_output['species'])[['taxonid', 'scientific_name', 'category']]
countries_df = df_output.join(df_normalized).dropna()

# Load your JSON file
with open("common_groups.json", "r") as file:
    data = json.load(file)

# Initialize an empty list to store DataFrames
df_list = []

# Loop through each group in the data
for group_name, species_list in data.items():
    # Normalize the list of species in the group
    group_df = pd.json_normalize(species_list)
    # Add a new column 'group' with the group name
    group_df['group'] = group_name
    # Append the DataFrame to the list
    df_list.append(group_df)

# Concatenate all the DataFrames into one
final_df = pd.concat(df_list, ignore_index=True)

final_df['taxonid'] = final_df['taxonid'].astype(int)
countries_df['taxonid'] = countries_df['taxonid'].astype(int)

merged_df = final_df.merge(countries_df[["full_name", "index", "taxonid"]], on="taxonid")

threatened_categories = ["CR"] 
threatened_df = merged_df[merged_df['category'].isin(threatened_categories)]

def get_common_name(scientific_name, api_key):
    url = f"https://apiv3.iucnredlist.org/api/v3/species/common_names/{str.lower(scientific_name)}?token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        if len(response.json()["result"])>0:
            primary_response = next((item['taxonname'] for item in response.json()["result"] if item['primary']), None)
            return primary_response
        else: return None
    else:
        return None

birds_CR = threatened_df[threatened_df["group"]=="birds"]

birds_CR["common_name"] = birds_CR['scientific_name'].progress_apply(lambda x: get_common_name(x, api_key))
birds_CR_grouped = birds_CR.groupby(["index", "full_name"]).agg(
    count=('taxonid', 'count'),
    scientific_names=('scientific_name', lambda x: list(x.unique())),
    common_names=('common_name', lambda x: list(x.unique()))
).reset_index()
birds_CR_grouped

birds_CR.to_csv("birds_CR.csv")
