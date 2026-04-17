import glob
import os
import json
from bs4 import BeautifulSoup
from tqdm import tqdm
import random
import hashlib

parsed_vega_lite_dir = "/Users/nngu0448/Documents/data/nvBench-dataset/nvBench_VegaLite_js"

def main_1():
    # html_glob_path = "/Users/nngu0448/Documents/data/nvBench-dataset/nvBench_VegaLite/*.html"
    # id_2_vega_lite = {}
    
    # html_paths = sorted(glob.glob(html_glob_path))
    # for html_path in tqdm(html_paths):

    #     ## extract ID
    #     nl_vis_id = None
    #     with open(html_path, "r", encoding="utf-8") as f:
    #         soup = BeautifulSoup(f, "html.parser")
        
    #     # Find the <b> tag with the exact text "(NL, VIS) ID: "
    #     target_b = soup.find("b", string="(NL, VIS) ID: ")

    #     if target_b:
    #         nl_vis_id = target_b.next_sibling.strip()
    #     assert nl_vis_id is not None, f"nl_vis_id is None for {html_path}"
        
    #     ## get Vega-Lite spec
    #     vegalite_path = os.path.join(parsed_vega_lite_dir, os.path.basename(html_path) + ".vega-lite.json")
    #     assert os.path.exists(vegalite_path), f"Vega-Lite spec not found for {html_path}"

    #     with open(vegalite_path, "r", encoding="utf-8") as f:
    #         vega_lite_spec = json.load(f)
    #         id_2_vega_lite[nl_vis_id] = vega_lite_spec
            
    # # Save the mapping to a JSON file
    # output_path = "/Users/nngu0448/Documents/data/nvBench-dataset/nlvis_id_2_vega_lite.json"
    # with open(output_path, "w", encoding="utf-8") as f:
    #     json.dump(id_2_vega_lite, f, ensure_ascii=False, indent=4)

    ## -----
    
    nlvis_id_2_vega_lite_path = "/Users/nngu0448/Documents/data/nvBench-dataset/nlvis_id_2_vega_lite.json"
    with open(nlvis_id_2_vega_lite_path, "r", encoding="utf-8") as f:
        nlvis_id_2_vega_lite = json.load(f)
        
    nvbench_content_path = "/Users/nngu0448/Documents/data/nvBench-dataset/NVBench.json"
    nvbench_data = json.load(open(nvbench_content_path, "r", encoding="utf-8"))
    
    data_samples = []
    not_found_ids = []
    
    for nlvis_id, value in tqdm(nvbench_data.items()):
        if nlvis_id not in nlvis_id_2_vega_lite:
            not_found_ids.append(nlvis_id)
            continue
        assert nlvis_id in nlvis_id_2_vega_lite, f"nlvis_id {nlvis_id} not found in nlvis_id_2_vega_lite"
        vql_query = value["vis_query"]["VQL"]
        chart = value["chart"]
        db_id = value["db_id"]
        hardness = value["hardness"]
        vegalite_spec = nlvis_id_2_vega_lite[nlvis_id]
        
        for nl_query in value["nl_queries"]:
            hexsha = hashlib.sha256((nlvis_id + "\n\n" + nl_query).encode("utf-8")).hexdigest()
            data_samples.append({
                "_id": nlvis_id + "\n\n" + nl_query,
                "nlvis_id": nlvis_id,
                "hexsha": hexsha,
                "chart": chart,
                "db_id": db_id,
                "hardness": hardness,
                "vis_query": vql_query,
                "nl_query": nl_query,
                "vega_lite_spec": json.dumps(vegalite_spec, ensure_ascii=False),
                "input_source": nl_query,
                "output_source": vql_query + "\n\n" + json.dumps(vegalite_spec, ensure_ascii=False),
                "content": json.dumps(vegalite_spec, ensure_ascii=False)
            })
        
    random.seed(42)
    random.shuffle(data_samples)
    # randomly take 1162 (val) + 3990 (test) samples
    data_samples = data_samples[:1162+3990]
    
    # Save to jsonl file
    jsonl_file_path = "/Users/nngu0448/Documents/data/nvBench-dataset/nvBench_val_test.jsonl"
    with open(jsonl_file_path, "w", encoding="utf-8") as f:
        for sample in data_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"number of not found ids: {len(not_found_ids)}")


if __name__ == "__main__":
    
    print()
    