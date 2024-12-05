
import json
import random
import pandas as pd
random.seed(42)

with open("data/iucn_species_countries.json", 'r') as f:
    data = json.load(f)

# Step 1: Collect all unique countries from the species data
all_countries = set()

for species_info in data.values():
    for country_info in species_info['countries']:
        all_countries.add((country_info['code'], country_info['country']))

# Convert the set back to a list for random sampling
all_countries = list(all_countries)

borders_df = pd.read_csv("../data/GEODATASOURCE-COUNTRY-BORDERS.CSV")

# Create a mapping of country codes to their bordering countries
border_dict = {}

for index, row in borders_df.iterrows():
    if row['country_border_code']:  # Check if there is a border country
        border_dict.setdefault(row['country_code'], []).append(row['country_border_code'])
        border_dict.setdefault(row['country_border_code'], []).append(row['country_code'])
country_dict = borders_df[['country_code', 'country_name']].drop_duplicates().set_index('country_code').to_dict()['country_name']

num_countries = 10
# Dictionary to hold the output
species_data = {}
# Process each species
for taxon_id, details in data.items():
    present_countries = details['countries']
    
    present_country_codes = {country["code"] for country in present_countries}
    nearby_country_codes = list({border for country in present_countries if country["code"] in border_dict for border in border_dict[country["code"]]}.difference(present_country_codes))
    
    num_present = num_countries//2
    selected_countries = random.sample(present_countries, k=min(num_present, len(present_countries)))
    selected_countries = [country["country"] for country in selected_countries]

    num_nearby = num_countries - len(selected_countries)
    selected_nearby = random.sample(nearby_country_codes, k=min(num_nearby, len(nearby_country_codes)))
    selected_nearby = [country_dict[code] for code in selected_nearby]

    num_random = num_countries - len(selected_countries) - len(selected_nearby)
    random.seed(int(taxon_id))  # Use the current time as the seed
    selected_random = random.sample([country[1] for country in all_countries if country[1] not in selected_countries + selected_nearby], num_random)

    # Combine selected countries
    combined_countries = selected_countries + selected_nearby + selected_random
    correct_answers = [1] * len(selected_countries) + [0] * (len(selected_nearby)+ len(selected_random))

    # Shuffle both lists together
    combined = list(zip(combined_countries, correct_answers))
    random.shuffle(combined)

    # Unzip the shuffled list back into locations and correct answers
    combined_countries, correct_answers = zip(*combined)
    
    # Store the combined data for this species in the final dictionary
    species_data[str(taxon_id)] = {
        "locations": list(combined_countries),
        "correct_answers": list(correct_answers)
    }

# Write the data to a JSON file
with open('task1_countries.json', 'w') as f:
    json.dump(species_data, f, indent=2)



