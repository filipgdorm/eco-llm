import csv
import json
import h3
import geopandas as gpd
import h3
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from shapely import Polygon

def plot_map(species_name, predicted_h3s, gt_h3s, out_path):
        # Load the world map shapefile
        world = gpd.read_file("data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")

        # Plot the world map
        ax = world.plot(color="lightgray")

        # Plot predicted h3s
        predicted_h3_polygons = [Polygon(h3.h3_to_geo_boundary(h, geo_json=True)) for h in predicted_h3s]
        gdf_predicted = gpd.GeoDataFrame(predicted_h3_polygons, columns=['geometry'])
        gdf_predicted.plot(ax=ax, color='red', alpha=0.3)

        # Plot the ground truth H3 cells
        gt_h3_polygons = [Polygon(h3.h3_to_geo_boundary(h, geo_json=True)) for h in gt_h3s]
        gdf_gt = gpd.GeoDataFrame(gt_h3_polygons, columns=['geometry'])
        gdf_gt.plot(ax=ax, color='green', alpha=0.3)

        # Combine bounds of the outline and H3 cells
        #combined_bounds = gpd.GeoSeries([outline_polygon] + gt_h3_polygons).total_bounds
        combined_bounds = gpd.GeoSeries(predicted_h3_polygons + gt_h3_polygons).total_bounds

        # Set the plot limits to match the combined bounding box of the polygons and H3 cells
        minx, miny, maxx, maxy = combined_bounds
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)

        blue_patch = mpatches.Patch(color='red', label='LLM Predicted Range')
        green_patch = mpatches.Patch(color='green', label='Ground Truth Range')
        plt.legend(handles=[blue_patch, green_patch])

        plt.title(species_name)
        plt.savefig(f"{out_path}/{species_name}.pdf", bbox_inches="tight")

def task2_eval(model_responses, eval_file_path="results/test_task2_gemini_responses1.json"):
    with open('data/gt_data/iucn_res_5.json', 'r') as f:
        range_data = json.load(f)
    # Open a CSV file for writing; will be created if it doesn't exist
    with open(eval_file_path.split('.')[0]+".csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Species", "F1"])

        f1scores = []
        invalid_responses = 0  # To count invalid model outputs
        
        for taxon_id, data in model_responses.items():
            response = data['response']
            try:
                # Step 1: Find the index of the first '[' and the last ']'
                start_index = response.find('{')
                end_index = response.rfind('}') + 1  # +1 to include the closing bracket

                # Step 2: Extract the substring containing just the list
                cleaned_response = response[start_index:end_index]

                # Attempt to parse the model's output
                outline = json.loads(cleaned_response)
                #Convert the polygon to GeoJSON format
                geojson_polygon = outline["features"][0]["geometry"]
                # Fill the polygon with H3 cells
                predicted_h3s = h3.polyfill_geojson(geojson_polygon, 5)

                coordinates = np.array(range_data['locs'])[np.array(range_data['taxa_presence'][taxon_id])]
                gt_h3s = []
                # Iterate through each coordinate
                for lon, lat in coordinates:
                    # Get the H3 index at resolution 5
                    h3_index = h3.geo_to_h3(lat, lon, 5)
                    gt_h3s.append(h3_index)

                # Convert list to a set to get unique H3 indices
                gt_h3s = set(gt_h3s)

                #calculate F1 score
                TP = len(predicted_h3s.intersection(gt_h3s))
                FP = len(predicted_h3s.difference(gt_h3s))
                FN = len(gt_h3s.difference(predicted_h3s))

                f1score = TP / (TP + 0.5*(FP+FN))

                #plot_map(taxon_id, predicted_h3s, gt_h3s, "results/plots/")

            except (ValueError, SyntaxError):
                # If parsing fails, count as an invalid response and set scores to 0
                print("Invalid model output format.")
                invalid_responses += 1
                f1score = None

            print("F1 Score: ", f1score)
            print("-" * 50)  # Separator for readability

            f1scores.append(f1score)
            writer.writerow([taxon_id, f1score])
        
        # Filter out None values (instead of using 'not None')
        valid_f1scores = [score for score in f1scores if score is not None]

        # Calculate the mean of valid (non-None) f1scores
        mean_f1scores = sum(valid_f1scores) / len(valid_f1scores) if valid_f1scores else 0.0

        print(f"Mean F1: {mean_f1scores}")
        print(f"Number of invalid model outputs: {invalid_responses}")
