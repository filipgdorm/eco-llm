import json
import random
import numpy as np
from tqdm import tqdm
import h3

with open("../../data/gt_data/iucn_res_5.json", 'r') as f:
    data = json.load(f)

with open("../../data/meta_data/iucn_species_names.json", "r") as file:
    species_names = json.load(file)

random.seed(42)  # You can use any integer value here
# Number of locations to pick for presence and absence
num_total_locations = 5

# Convert taxa_presence indices to actual locations
locs = data['locs']
species_data = {}
for taxon_id, indices in data['taxa_presence'].items():
    # Get the locations where the species is present
    present_locs = [data['locs'][i] for i in indices]

    # Get all possible indices and exclude the ones where the species is present
    all_indices = set(range(len(data['locs'])))
    absent_indices = list(all_indices - set(indices))
    absent_locs = [data['locs'][i] for i in absent_indices]

    h3_cells_res5 = {h3.geo_to_h3(lon, lat, 5) for lat, lon in present_locs}
    h3_cells_res3 = {h3.geo_to_h3(lon, lat, 3) for lat, lon in present_locs}
    # Step 2 & 3: For each H3 cell of resolution 3, get all H3 cells of resolution 5
    total_h3_cells = set()
    for cell in h3_cells_res3:
        res5_cells = h3.h3_to_children(cell, 5)
        total_h3_cells.update(res5_cells)

    absent_close_h3 = total_h3_cells.difference(h3_cells_res5)
    absent_close_coords = [h3.h3_to_geo(cell) for cell in absent_close_h3]
    flipped_close_absent_coords = [[lon, lat] for lat, lon in absent_close_coords]

    # Randomly select the locations
    selected_present_locs = random.sample(present_locs, 5)
    selected_close_absent_locs = random.sample(flipped_close_absent_coords, 2)
    selected_absent_locs = random.sample(absent_locs, 3)

    # Combine the locations and correct answers
    combined_locs = selected_present_locs + selected_close_absent_locs + selected_absent_locs
    correct_answers = [1] * 5 + [0] * 5

    # Shuffle both lists together
    combined = list(zip(combined_locs, correct_answers))
    random.shuffle(combined)

    # Unzip the shuffled list back into locations and correct answers
    combined_locs, correct_answers = zip(*combined)

    #round
    combined_locs = [[round(float(coord), 6) for coord in loc] for loc in combined_locs]

    # Store the combined data for this species in the final dictionary
    species_data[str(taxon_id)] = {
        "locations": list(combined_locs),
        "correct_answers": list(correct_answers)
    }

# Write the data to a JSON file
with open('task1_coordinates.json', 'w') as f:
    json.dump(species_data, f, indent=2)
