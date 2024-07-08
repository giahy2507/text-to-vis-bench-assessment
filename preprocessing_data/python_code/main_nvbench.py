from bs4 import BeautifulSoup
import re
import json
import glob
import os
from tqdm import tqdm
from main_vegalite import main_vegalite_parsing_from_the_stack

def nvbench_to_thestack(nvbench_dir, the_stack_output_path):
    paths = glob.glob(f'{nvbench_dir}/nvBench_VegaLite/*.html')

    os.makedirs(os.path.dirname(the_stack_output_path), exist_ok=True)
    fo = open(the_stack_output_path, mode="w", encoding="utf-8")

    for path in tqdm(paths):
        file_name = os.path.basename(path)

        # Read the HTML file
        with open(path, 'r') as file:
            html_content = file.read()

        # Create a BeautifulSoup object
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all script tags
        script_tags = soup.find_all('script')

        # Print the content of each script tag
        for i, script in enumerate(script_tags):
            text = script.get_text().strip()
            if text == "":
                continue

            seqs = re.split("// Embed the visualization", text)
            vlspec1 = seqs[0].strip().replace("var vlSpec1  =", "").replace(";", "").replace("\'", "\"")
            json_data = json.loads(vlspec1)
            json_data["$schema"] = "https://vega.github.io/schema/vega-lite/v4.json"

            hexsha = f"{file_name}_{i}"
            content = json.dumps(json_data)
            fo.write(json.dumps({"hexsha": hexsha, "content": content}) + "\n")

    

if __name__ == "__main__":

    # Download nvBench 
    # https://github.com/TsinghuaDatabaseGroup/nvBench
    # and save as "data/raw-data/nvBench"
    nvbench_dir = "/Users/nngu0448/Documents/data/nvBench"

    the_stack_output_path = "data/raw-data/nvBench/nvBench_VegaLite.the-stack.jsonl"
    nvbench_to_thestack(nvbench_dir, the_stack_output_path)

    universal_output_path = "data/universal/nvBench_Vegalite_Vega.universal2.jsonl"
    main_vegalite_parsing_from_the_stack(the_stack_output_path, universal_output_path)




