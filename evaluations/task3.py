import re
import ast
import csv

def task3_eval(model_responses, eval_file_path="results/test_task2_gemini_responses1.json"):
    # Function to normalize the species names (lowercase and remove hyphens)
    def normalize(name):
        return re.sub(r'[-\s]', '', name.lower())

    def parse_string_to_list(s):
        # Try using ast.literal_eval for quoted string lists
        try:
            return ast.literal_eval(s.strip())
        except (ValueError, SyntaxError):
            # Fallback for unquoted lists
            cleaned_string = s.strip().strip("[]")
            return [item.strip() for item in cleaned_string.split(",")]

    # Open a CSV file for writing; will be created if it doesn't exist
    with open(eval_file_path.split('.')[0]+".csv", mode='w', newline='') as file:
        writer = csv.writer(file)
    
        # Write the header row
        writer.writerow(["iso", "Precision", "Recall", "F1"])  # Added F1 to the header

        precisions = []
        recalls = []
        f1_scores = []  # For storing F1-scores
        invalid_responses = 0  # To count invalid model outputs

        # Print each question along with correct answers
        for taxon_id, data in model_responses.items():
            correct_common_names = data['correct_common_names']
            response = data['response']

            try:
                # Step 1: Find the index of the first '[' and the last ']'
                start_index = response.find('[')
                end_index = response.rfind(']') + 1  # +1 to include the closing bracket

                # Step 2: Extract the substring containing just the list
                cleaned_response = response[start_index:end_index]
                cleaned_response_fixed = re.sub(r"(?<=[a-zA-Z])'(?=[a-zA-Z]{1})", "", cleaned_response)

                model_answers = parse_string_to_list(cleaned_response_fixed)

                print(f"Model Answers: {model_answers}")
                print(f"Correct Answers: {correct_common_names}")

                # Normalize both lists
                correct_normalized = {normalize(name) for name in correct_common_names}
                output_normalized = {normalize(name) for name in model_answers}

                print(correct_normalized)
                print(output_normalized)

                # Calculate precision and recall
                true_positives = correct_normalized & output_normalized  # Intersection
                precision = len(true_positives) / len(output_normalized) if output_normalized else 0
                recall = len(true_positives) / len(correct_normalized) if correct_normalized else 0

                # Calculate F1-score
                if precision + recall > 0:
                    f1 = 2 * (precision * recall) / (precision + recall)
                else:
                    f1 = 0

            except (ValueError, SyntaxError):
                # If parsing fails, count as an invalid response and set scores to 0
                print("Invalid model output format. Recording 0 for precision, recall, and F1.")
                model_answers = "Invalid output"
                precision = None
                recall = None
                f1 = None
                invalid_responses += 1

            precisions.append(precision)
            recalls.append(recall)
            f1_scores.append(f1)

            print(f"Precision: {precision}")
            print(f"Recall: {recall}")
            print(f"F1: {f1}")
            print("-" * 50)  # Separator for readability

            # Write the row of results to the CSV file
            writer.writerow([str(taxon_id), precision, recall, f1])

        # Filter out None values from precisions, recalls, and f1_scores
        valid_precisions = [x for x in precisions if x is not None]
        valid_recalls = [x for x in recalls if x is not None]
        valid_f1_scores = [x for x in f1_scores if x is not None]

        # Calculate mean, handling empty lists
        mean_precision = sum(valid_precisions) / len(valid_precisions) if valid_precisions else 0.0
        mean_recall = sum(valid_recalls) / len(valid_recalls) if valid_recalls else 0.0
        mean_f1 = sum(valid_f1_scores) / len(valid_f1_scores) if valid_f1_scores else 0.0

        print(f"Mean precision: {mean_precision}")
        print(f"Mean recall: {mean_recall}")
        print(f"Mean F1: {mean_f1}")
        print(f"Number of invalid model outputs: {invalid_responses}")