import json
import argparse
from methods import *
import random

from evaluations.task1 import task1_eval, task1_baselines
from evaluations.task2 import task2_eval
from evaluations.task3 import task3_eval
from evaluations.task4 import task4_eval, task4_baseline

random.seed(42)

#Choose the path to the responses you want to evaluate.
EVAL_FILE_PATH = f"results/task4/test_task4_v4_gpt_responses.json"

def parse_arguments():
    # First, parse only the 'task' argument
    parser = argparse.ArgumentParser(description="Script to compute performance metrics.")
    
    parser.add_argument(
        '--task',
        type=str,
        choices=["1a", "1b", "2", "3", "4", "5a", "5b"],  # Add more tasks if required
        default="1a",
        help="Choose which task to evaluate."
    )

    # Parse just the 'task' argument initially
    args, unknown = parser.parse_known_args()

    # If the task is '1a' or '1b', add the 'baseline' argument
    if args.task in ["1a", "1b"]:
        parser.add_argument(
            '--baseline',
            type=str,
            choices=["model","random", "always0", "always1"],
            default="model",
            help="Specify baseline method: 'random', 'always0', or 'always1'."
        )
    elif args.task in ["4"]:
        parser.add_argument(
            '--baseline',
            type=str,
            choices=["model","random"],
            default="model",
            help="Specify baseline method: 'random'."
        )
    # Now, fully parse all arguments (including baseline if applicable)
    args = parser.parse_args()

    return args


def main():
    args = parse_arguments()

    with open(EVAL_FILE_PATH) as f:
        model_responses = json.load(f)
    if args.task == "1a" or args.task == "1b":
        if args.baseline == "model":
            task1_eval(model_responses, EVAL_FILE_PATH)
        else:
            task1_baselines(model_responses,args.baseline)
    elif args.task == "2":
        task2_eval(model_responses, EVAL_FILE_PATH)
    elif args.task == "3":
        task3_eval(model_responses, EVAL_FILE_PATH)
    elif args.task == "4":
        if args.baseline == "model":
            task4_eval(model_responses, EVAL_FILE_PATH)
        else:
            task4_baseline(model_responses,args.baseline)   

if __name__ == "__main__":
    main()