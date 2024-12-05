import json
import pandas as pd
import google.generativeai as genai
from openai import OpenAI
import random
random.seed(42)

def query_model(llm, api_key, question):
    if llm == "gemini":
        genai.configure(api_key=api_key)
        # Setting the generation configuration, including the temperature
        generation_config = {
            'temperature': 0.0,  # Set temperature to 0 for deterministic output
        }
        #load model
        model = genai.GenerativeModel('gemini-1.5-pro-001')
        try:
            # Generate the response from the model
            response = model.generate_content(
                question,
                generation_config=generation_config,
            )
            # Try to extract the response text
            response_text = response.text
        except (ValueError, SyntaxError) as e:
            response_text = None
            print(f"Error extracting response text: {e}")
    elif llm == "gpt":
        client = OpenAI(
            # This is the default and can be omitted
            api_key=api_key,
        )
        try:
        # Use OpenAI's API to generate a response
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": question,  # Insert the generated question here
                    }
                ],
                model="gpt-4o-2024-05-13",
                temperature=0,  # Set the desired temperature
            )
            # Extract the message content from the response
            response_text = response.choices[0].message.content
            
        except (ValueError, SyntaxError) as e:
            response_text = None
            print(f"Error extracting response text: {e}")
    return response_text

with open('queries.json') as f:
    queries = json.load(f)

with open("data/meta_data/iucn_species_names.json", "r") as file:
    species_names = json.load(file)

def generate_question(key, data, task, version):
    template = queries[f"task{task}"][f"version{version}"]
    if task == "1a":
        common_name = species_names[key]["common_name"]
        scientific_name = species_names[key]["scientific_name"]
        locations_str = '\n'.join([f"{lat}, {lon}" for lon, lat in data["locations"]])
        return template.format(common_name=common_name, scientific_name=scientific_name, locations=locations_str)
    elif task == "1b":
        common_name = species_names[key]["common_name"]
        scientific_name = species_names[key]["scientific_name"]
        locations_str = locations_str = '\n'.join([f"{country}" for country in data["locations"]])
        return template.format(common_name=common_name, scientific_name=scientific_name, locations=locations_str)
    elif task == "2":
        common_name = species_names[key]["common_name"]
        scientific_name = species_names[key]["scientific_name"]
        return template.format(common_name=common_name, scientific_name=scientific_name)
    elif task == "3":
        return template.format(country=data["full_name"])
    elif task == "4":
        taxon_id = str(data["taxon_id"])
        common_name = species_names[taxon_id]["common_name"]
        scientific_name = species_names[taxon_id]["scientific_name"]
        threat_info_string = threat_code_description(data["threat_code"])
        return template.format(common_name=common_name,scientific_name=scientific_name, threats_description=data["threats_description"], threat_code_description=threat_info_string, code=data["threat_code"], title=data["title"])
    elif task == "5a" or task == "5b":
        taxon_id = str(data["inat_id"])
        common_name = species_names[taxon_id]["common_name"]
        scientific_name = species_names[taxon_id]["scientific_name"]
        return template.format(common_name=common_name,scientific_name=scientific_name, trait=data["trait"], unit=data["units"])

    
def samsple_threats_assessments():
    with open("task_data/task4/iucn_threats.json", 'r') as f:
        threats_json = json.load(f)

    # Variables to hold classified and unclassified species
    classified_species = {}
    # Iterate through each species in the JSON
    for species_id, species_data in threats_json.items():
        classified_threats = []
        
        for threat in species_data['threats']:
            if not (threat['severity'] in ['Unknown', None] or threat['scope'] in ['Unknown', None] or threat['timing'] in ['Unknown', None]):
                classified_threats.append(threat)
        
        # Add species to classified_species if it has classified threats
        if classified_threats:
            classified_species[species_id] = {
                **species_data,
                'threats': classified_threats
            }

    df = pd.DataFrame(classified_species).T

    df_output = df.explode('threats').reset_index()
    df_normalized = pd.json_normalize(df_output['threats'])
    df_normalized["threat_code"] = df_normalized["code"]
    df_normalized=df_normalized.drop(columns=["code"])
    threats_df = df_output.join(df_normalized)

    # Group by 'scope' and 'severity'
    grouped = threats_df.groupby(['scope', 'severity'])

    # Total number of rows we want to sample
    total_sample_size = 100

    # Calculate the number of unique combinations of 'scope' and 'severity'
    num_groups = len(grouped)

    # Calculate the target number of samples per group (rounded)
    samples_per_group = total_sample_size // num_groups

    # Initialize an empty list to store sampled data
    sampled_data = []

    # Step 1: Stratified sampling - Sample 'samples_per_group' from each group
    for group, data in grouped:
        # If the group has fewer rows than 'samples_per_group', sample all rows
        group_sample = data.sample(min(samples_per_group, len(data)), random_state=42)
        sampled_data.append(group_sample)

    # Step 2: Combine all sampled data into a single DataFrame
    sampled_species_threats = pd.concat(sampled_data).reset_index(drop=True)

    # Step 3: If we still don't have 100 rows, sample additional rows from the remaining data
    remaining_rows_needed = total_sample_size - len(sampled_species_threats)
    if remaining_rows_needed > 0:
        additional_sample = threats_df.sample(remaining_rows_needed, random_state=42)
        sampled_species_threats = pd.concat([sampled_species_threats, additional_sample]).reset_index(drop=True)

    # Optional: Modify the 'index' and 'taxon_id' columns as needed
    sampled_species_threats["taxon_id"] = sampled_species_threats["index"]
    sampled_species_threats["index"] = sampled_species_threats["index"].astype(str) + "_" + sampled_species_threats["threat_code"]
    print("Num species: ", len(sampled_species_threats))
    return sampled_species_threats

def get_task12_species():
    # Convert to DataFrame
    df_full = pd.DataFrame.from_dict(species_names, orient='index')
    df_full = df_full.reset_index()

    #make sure that the species we choose have countries associated with them
    with open("task_data/task1/task1_countries.json", 'r') as f:
            json_data = json.load(f)
    # Convert to DataFrame
    df_countries = pd.DataFrame.from_dict(json_data, orient='index')
    df_countries = df_countries.reset_index()
    species_w_countries = df_countries[df_countries['correct_answers'].apply(lambda x: sum(x) > 0)]
    df_full = df_full[df_full["index"].isin(species_w_countries["index"])]  # only consider species we have country info for

    # List of already chosen species codes
    chosen_codes = ["42888", "135104", "19284", "10717", "39579", "32944", "13270", "74831", "27123", "43339"]

    # Filter out chosen species from the DataFrame
    df_remaining = df_full[~df_full["index"].isin(chosen_codes)]

    # Count how many chosen species are in each class
    chosen_counts = df_full[df_full["index"].isin(chosen_codes)]['class_name'].value_counts()

    # Calculate how many more are needed in each class
    num_species_per_class = 25  # Total species per class
    species_needed = {cls: max(0, num_species_per_class - chosen_counts.get(cls, 0)) for cls in ['Mammalia', 'Reptilia', 'Amphibia', 'Aves']}

    # Sample the required number of species for each class
    mammals = df_remaining[df_remaining['class_name'] == 'Mammalia'].sample(n=species_needed['Mammalia'], random_state=42)
    reptiles = df_remaining[df_remaining['class_name'] == 'Reptilia'].sample(n=species_needed['Reptilia'], random_state=42)
    amphibians = df_remaining[df_remaining['class_name'] == 'Amphibia'].sample(n=species_needed['Amphibia'], random_state=42)
    birds = df_remaining[df_remaining['class_name'] == 'Aves'].sample(n=species_needed['Aves'], random_state=42)

    # Combine the sampled DataFrames with the already chosen species
    sampled_df = pd.concat([mammals, reptiles, amphibians, birds]).reset_index(drop=True)

    # Adding already chosen species to the final DataFrame
    chosen_species_df = df_full[df_full["index"].isin(chosen_codes)]
    final_df = pd.concat([chosen_species_df, sampled_df]).reset_index(drop=True)
    return final_df["index"].values


def threat_code_description(threat_code):
    with open("task_data/task4/threats_description.json", "r") as file:
        threats_description = json.load(file)
    # Split the threat_code by dots
    split_parts = threat_code.split(".")

    # Construct an incrementally growing list
    threat_list = []
    for i in range(len(split_parts)):
        threat_list.append(".".join(split_parts[:i + 1]))

    threat_info_list = []
    current_entry = threats_description
    # Traverse through the JSON structure based on the threat code parts
    for i, part in enumerate(threat_list):
            current_entry = current_entry[part]
            # Prepare the formatted string for the main category
            # Construct the threat_info string conditionally based on the existence of description and examples
            threat_info = f"Code: {part}, Name: '{current_entry['name']}'"

            # Add description if it exists
            if 'description' in current_entry and current_entry['description']:
                threat_info += f", Description: '{current_entry['description']}'"

            # Add examples if they exist
            if 'examples' in current_entry and current_entry['examples']:
                threat_info += f", Examples: '{current_entry['examples']}'"
            threat_info_list.append(threat_info)
            if "subcategories" in current_entry:
                    current_entry = current_entry["subcategories"]
    # Concatenate into a three-row string
    threat_info_string = "\n".join(threat_info_list)

    return threat_info_string