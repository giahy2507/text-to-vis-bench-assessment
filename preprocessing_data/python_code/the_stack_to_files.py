import os
import json
from tqdm import tqdm
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--thestack_jsonl_path", type=str)
    parser.add_argument("--thestack_output_dir", type=str)
    args = parser.parse_args()

    # thestack_jsonl_path = "data/raw-data/the-stack/JavaScript.chartjs.jsonl"
    # thestack_output_dir = "data/raw-data/the-stack/JavaScript_ChartJS"
    thestack_jsonl_path = args.thestack_jsonl_path
    thestack_output_dir = args.thestack_output_dir
    os.makedirs(thestack_output_dir, exist_ok=True)

    with open(thestack_jsonl_path, mode="r", encoding="utf-8") as fi:
        the_stack_lines = fi.readlines()
        for line in tqdm(the_stack_lines):
            if line.strip() != "":
                json_data = json.loads(line)

                hexsha = json_data["hexsha"]
                content = json_data["content"]
                extension = json_data["ext"]

                output_file_path = f"{thestack_output_dir}/{hexsha}.{extension}"
                with open(output_file_path, mode="w", encoding="utf-8") as fo:
                    fo.write(content)
                