import pandas as pd
import os
import json
from tqdm import tqdm
from parse_args import *
from methods import *
from dotenv import load_dotenv

args = parse_args()

OUT_PATH = f"results/task{args.task}/{args.exp_name}_task{args.task}_v{args.prompt_version}_{args.llm}_responses.json"

#get api key
load_dotenv()
if args.llm=="gemini": api_key=os.environ.get("GEMINI_API_KEY")
elif args.llm=="gpt": api_key=os.environ.get("OPENAI_API_KEY")

# Create the directory if it doesn't exist
output_directory = os.path.dirname(OUT_PATH)
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Check if the output file exists, if so, load existing data
if os.path.exists(OUT_PATH):
    with open(OUT_PATH, 'r') as infile:
        output_data = json.load(infile)
else:
    output_data = {}

with open("task_data/task1/task1_coordinates.json", 'r') as file:
    species_coordinates = json.load(file)
with open("task_data/task1/task1_countries.json", 'r') as file:
    species_countries = json.load(file)

if args.task == "1a":  
    keys = get_task12_species()
    keys_w_data = {species: species_coordinates[species] for species in species_coordinates if species in keys}
elif args.task == "1b":  
    keys = get_task12_species()
    keys_w_data = {species: species_countries[species] for species in species_countries if species in keys}   
elif args.task == "2":  
    keys = get_task12_species()
    keys_w_data = {key: None for key in keys}
elif args.task == "3":
    birds_CR = pd.read_csv("task_data/task3/birds_CR.csv", keep_default_na=False)
    birds_CR_grouped = birds_CR.groupby(["index", "full_name"]).agg(
        count=('taxonid', 'count'),
        scientific_names=('scientific_name', lambda x: list(x.unique())),
        common_names=('common_name', lambda x: list(x.unique()))
    ).reset_index()
    keys_w_data = birds_CR_grouped.set_index('index')[['common_names', 'full_name']].to_dict(orient='index')
    keys = keys_w_data.keys()
elif args.task == "4":
    sampled_species_threats = samsple_threats_assessments()
    # Create the dictionary with common_names, full_name, and correct_answers (scope + severity)
    keys_w_data = sampled_species_threats.set_index('index').apply(
        lambda row: {
            'taxon_id': row['taxon_id'],
            'threats_description': row['threats_description'],
            'threat_code': row['threat_code'],
            'title': row['title'],
            'correct_answers': [row['scope'], row['severity']]  # Combine scope and severity into a list
        }, axis=1
    ).to_dict()    
    keys = keys_w_data.keys()
elif args.task == "5a":
    bird_traits = pd.read_csv("task_data/task5/task5_bird_traits.csv",index_col="index")
    keys_w_data = bird_traits.to_dict(orient='index')
    keys = keys_w_data.keys()
elif args.task == "5b":  
    mammal_traits = pd.read_csv("task_data/task5/task5_mammal_traits.csv",index_col="index")
    keys_w_data = mammal_traits.to_dict(orient='index')
    keys = keys_w_data.keys()
  

for key in tqdm(keys):
    # Skip if if already processed
    if key in output_data.keys():
        print(f"Skipping {key}, already processed.")
        continue
    data = keys_w_data[key]
    question = generate_question(key, data, args.task, args.prompt_version)
    response = query_model(args.llm, api_key, question)

    if data is not None: correct_answers = data.get("correct_answers", [])
    else: correct_answers = None
    output_data[key] = {
        "question": question,
        "response": response,
        "correct_answers": correct_answers
    }
    with open(OUT_PATH, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)


