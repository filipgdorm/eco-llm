import pandas as pd
import json
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import numpy as np

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)


#############
#Bird Traits#
#############

# Parse JSON data
with open("../../data/meta_data/iucn_species_names.json") as f:
    json_dict = json.load(f)

# Create mapping of scientific names to common names and inat_id
species_to_info = {
    info["scientific_name"]: {"common_name": info["common_name"], "inat_id": key}
    for key, info in json_dict.items()
}

# Function to map species to common name and inat_id
def add_common_inat(row):
    species = row['Species1']
    if species in species_to_info:
        return pd.Series([species_to_info[species]['common_name'], species_to_info[species]['inat_id']])
    else:
        return pd.Series([None, None])

avonet_df = pd.read_csv("AVONET/TraitData/AVONET1_BirdLife.csv")

avonet_df[['common_name', 'inat_id']] = avonet_df.apply(add_common_inat, axis=1)

avonet_df_subset = avonet_df[["inat_id", "common_name", "Species1", "Beak.Length_Culmen", 'Wing.Length', 'Tail.Length', 'Mass']].dropna()

numerical_data = avonet_df_subset[["Beak.Length_Culmen",	"Wing.Length",	"Tail.Length",	"Mass"]]
# Step 1: Normalize the numerical data
scaler = StandardScaler()
normalized_data = scaler.fit_transform(numerical_data)

# Step 2: Sample 100 species randomly
n_samples = 100  # You want to sample 100 species
selected_avonet_species = avonet_df_subset.sample(n=n_samples, random_state=RANDOM_SEED)

# Rename Species1 to scientific_name
selected_avonet_species = selected_avonet_species.rename(columns={'Species1': 'scientific_name'})

# Restructure DataFrame using pd.melt
melted_df = pd.melt(
    selected_avonet_species, 
    id_vars=['inat_id', 'common_name', 'scientific_name'], 
    value_vars=['Beak.Length_Culmen', 'Wing.Length', 'Tail.Length', 'Mass'],
    var_name='trait',
    value_name='correct_answers'
)

# Mapping traits and units
trait_map = {
    'Beak.Length_Culmen': 'beak length', 
    'Wing.Length': 'wing length', 
    'Tail.Length': 'tail length', 
    'Mass': 'mass'
}
unit_map = {
    'beak length': 'millimeters',
    'wing length': 'millimeters',
    'tail length': 'millimeters',
    'mass': 'grams'
}

# Apply trait map
melted_df['trait'] = melted_df['trait'].map(trait_map)

# Add units column
melted_df['units'] = melted_df['trait'].map(unit_map)

# Concatenate inat_id and trait to create a new index
melted_df['index'] = melted_df['inat_id'].astype(str) + '_' + melted_df['trait']

# Set the new concatenated column as the index
melted_df = melted_df.set_index('index')

melted_df.to_csv("task5_bird_traits.csv")

################
#Mammals Traits#
################

combine_df = pd.read_csv("COMBINE/COMBINE_archives/trait_data_imputed.csv")

# Function to map species to common name and inat_id
def add_common_inat2(row):
    species = row['iucn2020_binomial']
    if species in species_to_info:
        return pd.Series([species_to_info[species]['common_name'], species_to_info[species]['inat_id']])
    else:
        return pd.Series([None, None])
    
combine_df[['common_name', 'inat_id']] = combine_df.apply(add_common_inat2, axis=1)

combine_df_subset = combine_df[["inat_id", "common_name", "iucn2020_binomial", "adult_body_length_mm", 'gestation_length_d', 'max_longevity_d', 'adult_mass_g']].dropna()

numerical_data = combine_df_subset[["adult_body_length_mm", 'gestation_length_d', 'max_longevity_d', 'adult_mass_g']]
# Step 1: Normalize the numerical data
scaler = StandardScaler()
normalized_data = scaler.fit_transform(numerical_data)

# Step 2: Sample 100 species randomly
n_samples = 100  # You want to sample 100 species
selected_combine_species = combine_df_subset.sample(n=n_samples, random_state=RANDOM_SEED)
selected_combine_species = selected_combine_species.rename(columns={'iucn2020_binomial': 'scientific_name'})

# Restructure DataFrame using pd.melt
melted_df = pd.melt(
    selected_combine_species, 
    id_vars=['inat_id', 'common_name', 'scientific_name'], 
    value_vars=['adult_body_length_mm', 'gestation_length_d', 'max_longevity_d', 'adult_mass_g'],
    var_name='trait',
    value_name='correct_answers'
)

# Mapping traits and units
trait_map = {
    'adult_body_length_mm': 'adult body length', 
    'gestation_length_d': 'gestation length', 
    'max_longevity_d': 'max longevity', 
    'adult_mass_g': 'adult mass'
}
unit_map = {
    'adult body length': 'millimeters',
    'gestation length': 'days',
    'max longevity': 'days',
    'adult mass': 'grams'
}

# Apply trait map
melted_df['trait'] = melted_df['trait'].map(trait_map)

# Add units column
melted_df['units'] = melted_df['trait'].map(unit_map)

# Concatenate inat_id and trait to create a new index
melted_df['index'] = melted_df['inat_id'].astype(str) + '_' + melted_df['trait']

# Set the new concatenated column as the index
melted_df = melted_df.set_index('index')

melted_df.to_csv("task5_mammal_traits.csv")
