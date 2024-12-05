import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Script to obtain answers from LLMs.")
    parser.add_argument(
        '--llm',
        type=str,
        choices=['gemini', 'gpt'],  # add more models if required
        default='gemini',
        help="Choose the LLM to evaluate."
    )
    parser.add_argument(
        '--task',
        type=str,
        choices=["1a","1b","2", "3", "4", "5a", "5b"],  # add more tasks if required
        default="1a",
        help="Choose what task to evaluate."
    )
    parser.add_argument(
        '--prompt_version',
        type=int,
        default=1,
        help="Choose what version of prompt to use."
    )
    parser.add_argument(
        "--exp_name", 
        type=str, 
        default='test', 
        help="Experiment name, also the dir where thresholds will be collected from."
    )

    # Parse the arguments
    args = parser.parse_args()

    return args