import re
import csv
import random

# Define similarity function for scope
def scope_similarity(predicted, correct):
    scope_mapping = {
        "Whole": 3,
        "Majority": 2,
        "Minority": 1
    }
    
    if predicted == correct:
        return 1.0  # Exact match
    
    diff = abs(scope_mapping[predicted] - scope_mapping[correct])
    
    if diff == 1:
        return 0.5  # Adjacent categories
    else:
        return 0.0  # Far apart

# Define similarity function for severity
def severity_similarity(predicted, correct):
    severity_mapping = {
        "Very Rapid Declines": 6,
        "Rapid Declines": 5,
        "Slow, Significant Declines": 4,
        "Causing/Could cause fluctuations": 3,
        "Negligible declines": 2,
        "No decline": 1
    }
    
    if predicted == correct:
        return 1.0  # Exact match
    
    diff = abs(severity_mapping[predicted] - severity_mapping[correct])
    
    if diff == 1:
        return 0.75  # Close match
    elif diff == 2:
        return 0.5  # Intermediate match
    elif diff == 3:
        return 0.25  # Distant match
    else:
        return 0.0  # Opposite end

# Calculate overall fuzzy score
def fuzzy_score(predicted_scope, predicted_severity, correct_scope, correct_severity):
    scope_score = scope_similarity(predicted_scope, correct_scope)
    severity_score = severity_similarity(predicted_severity, correct_severity)
    
    return {
        'Scope Fuzzy': scope_score,
        'Severity Fuzzy': severity_score
    }

def compute_accuracy(predicted_scope, predicted_severity, correct_scope, correct_severity):
    """
    Compute the accuracy for timing, scope, and severity separately.
    
    :param correct_answers: List of correct answers in the format [timing, scope, severity].
    :param model_answers: List of model's answers in the format [timing, scope, severity].
    :return: Dictionary with accuracy percentages for timing, scope, and severity.
    """
    
    # Check scope accuracy (only consider leftmost word, do not care about percentages expressed in parentheses)
    scope_accuracy=int(correct_scope == predicted_scope)
    
    # Check severity accuracy
    severity_accuracy=int(correct_severity == predicted_severity)

    
    # Return the accuracies
    return {
        'Scope Accuracy': scope_accuracy,
        'Severity Accuracy': severity_accuracy
    }

def parse_string(input_string):
    # Define regex to capture the content inside square brackets
    pattern = r"\[(.*?)\]"  # Matches anything inside square brackets
    match = re.search(pattern, input_string)
    
    if match:
        content = match.group(1).strip()
        
        # Split the content at the first comma only
        scope, severity = re.split(r',\s*(?![^\(\)]*\))', content, maxsplit=1)
        
        # Remove any single or double quotes and strip leading/trailing whitespace
        scope = scope.strip().replace("'", "").replace('"', '')
        severity = severity.strip().replace("'", "").replace('"', '')
        
        return scope, severity

def task4_eval(model_responses, eval_file_path):
    with open(eval_file_path.split('.')[0]+".csv", mode='w', newline='') as file:
        writer = csv.writer(file)
    
        # Write the header row
        writer.writerow(["Species", "Scope Accuracy", "Severity Accuracy", "Scope Fuzzy", "Severity Fuzzy"])

        scope_accs = []
        sev_accs = []
        scope_fuzz = []
        sev_fuzz = []
        invalid_responses = 0  # To count invalid model outputs
        
        # Iterate over the model responses
        for key, data in model_responses.items():
            correct_answers = data['correct_answers']
            response = data['response']
            print("-" * 50)
            print("Correct answers: ", correct_answers)
            print("Model answers: ", response)
            
            try:
                # Parse the response
                predicted_scope, predicted_severity = parse_string(response)

                # Compute accuracy and fuzzy score
                accuracy = compute_accuracy(predicted_scope.split()[0], predicted_severity, correct_answers[0].split()[0], correct_answers[1])
                fuzzy = fuzzy_score(predicted_scope.split()[0], predicted_severity, correct_answers[0].split()[0], correct_answers[1])

                print(accuracy)
                print(fuzzy)

                # Append accuracy and fuzzy scores to the lists
                scope_accs.append(accuracy['Scope Accuracy'])
                sev_accs.append(accuracy['Severity Accuracy'])
                scope_fuzz.append(fuzzy['Scope Fuzzy'])
                sev_fuzz.append(fuzzy['Severity Fuzzy'])

                # Write the data to the CSV file
                writer.writerow([str(key), 
                                accuracy['Scope Accuracy'], accuracy['Severity Accuracy'], 
                                fuzzy['Scope Fuzzy'], fuzzy['Severity Fuzzy']])
            except (ValueError, SyntaxError):
                # If parsing fails, handle invalid response
                print("Invalid model output format. Recording 0..")
                invalid_responses += 1

                # Append zeros for invalid responses
                scope_accs.append(0)
                sev_accs.append(0)
                scope_fuzz.append(0)
                sev_fuzz.append(0)

                # Write zeros for invalid responses
                writer.writerow([str(key), None, None, None, None])


    # Calculate and print average accuracy and fuzzy scores
    if len(scope_accs) > 0:
        print("Scope accuracy: ", sum(scope_accs) / len(scope_accs))
        print("Severity accuracy: ", sum(sev_accs) / len(sev_accs))

    if len(scope_fuzz) > 0:
        print("Scope fuzzy score: ", sum(scope_fuzz) / len(scope_fuzz))
        print("Severity fuzzy score: ", sum(sev_fuzz) / len(sev_fuzz))

    # Print total invalid responses
    print(f"Total invalid responses: {invalid_responses}")

def task4_baseline(model_responses, eval_file_path):
    with open(eval_file_path.split('.')[0]+".csv", mode='w', newline='') as file:
        writer = csv.writer(file)
    
        # Write the header row
        writer.writerow(["Species", "Scope Accuracy", "Severity Accuracy", "Scope Fuzzy", "Severity Fuzzy"])

        scope_accs = []
        sev_accs = []
        scope_fuzz = []
        sev_fuzz = []
        invalid_responses = 0  # To count invalid model outputs
        
        # Iterate over the model responses
        for key, data in model_responses.items():
            correct_answers = data['correct_answers']
            print("-" * 50)
            print("Correct answers: ", correct_answers)

            scope_answers = ["Whole", "Majority", "Minority"]
            severity_answers = ["Very Rapid Declines", "Rapid Declines", "Slow, Significant Declines", "Causing/Could cause fluctuations", "Negligible declines" , "No decline"]

            model_answers = [random.choice(scope_answers), random.choice(severity_answers)]
            print("Model answers: ", model_answers)
            

            predicted_scope, predicted_severity = model_answers

            # Compute accuracy and fuzzy score
            accuracy = compute_accuracy(predicted_scope.split()[0], predicted_severity, correct_answers[0].split()[0], correct_answers[1])
            fuzzy = fuzzy_score(predicted_scope.split()[0], predicted_severity, correct_answers[0].split()[0], correct_answers[1])

            print(accuracy)
            print(fuzzy)

            # Append accuracy and fuzzy scores to the lists
            scope_accs.append(accuracy['Scope Accuracy'])
            sev_accs.append(accuracy['Severity Accuracy'])
            scope_fuzz.append(fuzzy['Scope Fuzzy'])
            sev_fuzz.append(fuzzy['Severity Fuzzy'])

            # Write the data to the CSV file
            writer.writerow([str(key), 
                            accuracy['Scope Accuracy'], accuracy['Severity Accuracy'], 
                            fuzzy['Scope Fuzzy'], fuzzy['Severity Fuzzy']])

    # Calculate and print average accuracy and fuzzy scores
    print("Scope accuracy: ", sum(scope_accs) / len(scope_accs))
    print("Severity accuracy: ", sum(sev_accs) / len(sev_accs))

    print("Scope fuzzy score: ", sum(scope_fuzz) / len(scope_fuzz))
    print("Severity fuzzy score: ", sum(sev_fuzz) / len(sev_fuzz))
