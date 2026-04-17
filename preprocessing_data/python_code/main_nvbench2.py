from bs4 import BeautifulSoup
import re
import json
import glob
import os
from tqdm import tqdm
from main_vegalite import main_vegalite_parsing_from_the_stack

def nvbench_to_thestack(nvbench_dir, the_stack_output_path):
    test_json_path = f"{nvbench_dir}/test.json"
    all_data = json.load(open(test_json_path, "r", encoding="utf-8"))

    os.makedirs(os.path.dirname(the_stack_output_path), exist_ok=True)
    fo = open(the_stack_output_path, mode="w", encoding="utf-8")

    for idx, item in enumerate(all_data):
        vlspec1 = item["gold_answer"]
        json_data = json.loads(vlspec1)
        for j, output_option in enumerate(json_data):
            output_option["$schema"] = "https://vega.github.io/schema/vega-lite/v4.json"
            
            sample_id = f"test_" + str(idx).zfill(5) + f"_{j}"
            hexsha = sample_id
            content = json.dumps(json_data)
            fo.write(json.dumps({"hexsha": hexsha, "content": content}) + "\n")

    

if __name__ == "__main__":

    # Download nvBench 
    # https://github.com/TsinghuaDatabaseGroup/nvBench
    # and save as "data/raw-data/nvBench"
    nvbench_dir = "/Users/nngu0448/Documents/data/nvBench2.0-dataset"

    the_stack_output_path = "data/raw-data/nvBench/nvBench2_VegaLite.the-stack.jsonl"
    nvbench_to_thestack(nvbench_dir, the_stack_output_path)

    universal_output_path = "data/universal_phase2/nvBench2_VegaLite_Vega.universal2.jsonl"
    main_vegalite_parsing_from_the_stack(the_stack_output_path, universal_output_path)




