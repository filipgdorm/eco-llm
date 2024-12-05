import csv
import ast
from sklearn.metrics import accuracy_score, precision_recall_curve, auc, roc_auc_score, average_precision_score
import random
random.seed(42)

def task1_eval(model_responses, eval_file_path="results/test_task2_gemini_responses1.json"):
    # Open a CSV file for writing; will be created if it doesn't exist
    with open(eval_file_path.split('.')[0]+".csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(["Species", "Accuracy", "AUC PR", "AUC ROC", "Average Precision"])  # Added Average Precision to the header

        accuracies = []
        auc_prs = []
        auc_rocs = []  # List to store AUC ROC values
        average_precisions = []  # List to store Average Precision values
        invalid_responses = 0  # To count invalid model outputs
        species_count = 0  # Counter for species processed

        # Print each question along with correct answers
        for taxon_id, data in model_responses.items():
            correct_answers = data['correct_answers']
            if sum(correct_answers) == 0:
                continue
            response = data['response']

            try:
                # Step 1: Find the index of the first '[' and the last ']'
                start_index = response.find('[')
                end_index = response.rfind(']') + 1  # +1 to include the closing bracket

                # Step 2: Extract the substring containing just the list
                cleaned_response = response[start_index:end_index]
                # Attempt to parse the model's output
                model_answers = ast.literal_eval(cleaned_response)

                print(f"Model Answers: {model_answers}")
                print(f"Correct Answers: {correct_answers}")

                # Binarizing model predictions for accuracy calculation
                binarized_model_answers = [1 if x >= 0.5 else 0 for x in model_answers]

                # Calculating Accuracy
                accuracy = accuracy_score(correct_answers, binarized_model_answers)

                # Calculating AUC PR
                precision, recall, _ = precision_recall_curve(correct_answers, model_answers)
                auc_pr = auc(recall, precision)

                # Calculating AUC ROC
                auc_roc = roc_auc_score(correct_answers, model_answers)

                # Calculating Average Precision
                average_precision = average_precision_score(correct_answers, model_answers)

            except (ValueError, SyntaxError):
                # If parsing fails, count as an invalid response and set scores to 0
                print("Invalid model output format. Recording 0 for accuracy and MAP.")
                model_answers = "Invalid output"
                accuracy = None
                auc_pr = None
                auc_roc = None  # Set AUC ROC to None in case of error
                average_precision = None  # Set Average Precision to None in case of error
                invalid_responses += 1

            # Store the metrics
            accuracies.append(accuracy)
            auc_prs.append(auc_pr)
            auc_rocs.append(auc_roc)  # Append None for AUC ROC
            average_precisions.append(average_precision)  # Append Average Precision

            print(f"Accuracy: {accuracy}")
            print(f"AUC PR: {auc_pr}")
            print(f"AUC ROC: {auc_roc}")  # Print AUC ROC
            print(f"Average Precision: {average_precision}")  # Print Average Precision
            print("-" * 50)  # Separator for readability

            # Write the row of results to the CSV file
            writer.writerow([str(taxon_id), accuracy, auc_pr, auc_roc, average_precision])  # Include Average Precision in the output

            # Increment the species counter
            species_count += 1

        # Filter out None values from metrics
        valid_accuracies = [acc for acc in accuracies if acc is not None]
        valid_auc_prs = [auc for auc in auc_prs if auc is not None]
        valid_auc_rocs = [auc for auc in auc_rocs if auc is not None]  # Filter AUC ROC values
        valid_average_precisions = [ap for ap in average_precisions if ap is not None]  # Filter Average Precision values

        # Calculate mean, handling empty lists
        mean_accuracy = sum(valid_accuracies) / len(valid_accuracies) if valid_accuracies else 0.0
        mean_auc_pr = sum(valid_auc_prs) / len(valid_auc_prs) if valid_auc_prs else 0.0
        mean_auc_roc = sum(valid_auc_rocs) / len(valid_auc_rocs) if valid_auc_rocs else 0.0  # Calculate mean AUC ROC
        mean_average_precision = sum(valid_average_precisions) / len(valid_average_precisions) if valid_average_precisions else 0.0  # Calculate mean Average Precision

        print(f"Mean accuracy: {mean_accuracy}")
        print(f"Mean AUC PR: {mean_auc_pr}")
        print(f"Mean AUC ROC: {mean_auc_roc}")  # Print mean AUC ROC
        print(f"Mean Average Precision: {mean_average_precision}")  # Print mean Average Precision
        print(f"Number of invalid model outputs: {invalid_responses}")

def task1_baselines(model_responses, task1_baseline):
    accuracies = []
    average_precisions = []  # List to store Average Precision values
    for _, data in model_responses.items():
        correct_answers = data['correct_answers']
        
        # Simulating model answers with random probabilities
        if task1_baseline == "random":
            model_answers = [random.random() for _ in range(10)]
        elif task1_baseline == "always0":
            model_answers = [0]*10
        elif task1_baseline == "always1":
            model_answers = [1]*10  # Corrected this line to always predict 1

        # Binarizing model predictions for accuracy calculation
        binarized_model_answers = [1 if x >= 0.5 else 0 for x in model_answers]

        # Calculating Accuracy
        accuracy = accuracy_score(correct_answers, binarized_model_answers)
        accuracies.append(accuracy)

        # Calculating Average Precision
        average_precision = average_precision_score(correct_answers, model_answers)
        average_precisions.append(average_precision)

    # Calculate and print the mean accuracy, AUC PR, AUC ROC, and Average Precision scores
    mean_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
    mean_average_precision = sum(average_precisions) / len(average_precisions) if average_precisions else 0.0  # Calculate mean Average Precision

    print(f"Mean accuracy: {mean_accuracy}")
    print(f"Mean Average Precision: {mean_average_precision}")  # Print mean Average Precision
