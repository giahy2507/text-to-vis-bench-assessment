import os
from utils import get_file_length
from tqdm import tqdm
import json


import json
import glob
import re
from collections import defaultdict, OrderedDict
import os
import shutil
from pprint import pprint

vegalite_list_schema_list = {
        "v5": "https://vega.github.io/schema/vega-lite/v5.json",
        "v4": "https://vega.github.io/schema/vega-lite/v4.json",
        "v3": "https://vega.github.io/schema/vega-lite/v3.json",
        "v2": "https://vega.github.io/schema/vega-lite/v2.json",
        "v1": "https://vega.github.io/schema/vega-lite/v1.json",
    }
vegalist_schema_list = [value for _, value in vegalite_list_schema_list.items()]


def detect_vegalite_version(json_data):    
    for key, value in vegalite_list_schema_list.items():
        if value in json_data:
            return key
    return None


def flatten_json(json_data, parent_key='', sep='|'):
    items = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, (dict, list)):
                items.extend(flatten_json(value, new_key, sep=sep))
            else:
                items.append((new_key, value))
    elif isinstance(json_data, list):
        for index, item in enumerate(json_data):
            new_key = f"{parent_key}[{index}]"
            if isinstance(item, (dict, list)):
                items.extend(flatten_json(item, new_key, sep=sep))
            else:
                items.append((new_key, item))
    return items


def recursive_extract_vegalite_component(json_data):
    if isinstance(json_data, dict) and "$schema" in json_data:
        if json_data["$schema"] in vegalist_schema_list:
            return [json_data]
        else:
            return []
    else:
        if isinstance(json_data, dict):
            result = []
            for k, v in json_data.items():
                if isinstance(v, dict):
                    result += recursive_extract_vegalite_component(v)
                elif isinstance(v, list):
                    for item in v:
                        result += recursive_extract_vegalite_component(item)
                else:
                    continue
            return result
        elif isinstance(json_data, list):
            result = []
            for item in json_data:
                result += recursive_extract_vegalite_component(item)
            return result
        else:
            return []

def main_vegalite_parsing_from_the_stack(jsonl_file_path, output_file_path):
    assert os.path.exists(jsonl_file_path), f"{jsonl_file_path} does not exist"
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    fo = open(output_file_path, mode="w", encoding="utf-8")

    num_lines = get_file_length(jsonl_file_path)
    with open(jsonl_file_path, mode="r", encoding="utf-8") as fi:
        for line in tqdm(fi, total=num_lines):
            if line.strip() != "":
                try: 
                    json_data = json.loads(line.strip())
                    if not detect_vegalite_version(json_data["content"]):
                        print("Not a vega-lite schema")
                        continue

                    hexsha = json_data["hexsha"]
                    content = json.loads(json_data["content"])
                    universal_items = []

                    vegalite_items = recursive_extract_vegalite_component(content)
                    for i, vegalite_item in enumerate(vegalite_items):
                        # detect vega version
                        vegalite_definition_dict = OrderedDict()
                        flattened_list = flatten_json(vegalite_item)
                        for key, value in flattened_list:
                            p_key = re.sub(r'\[\d+\]', '', key)
                            p_key = re.sub("(spec\|)|(concat\|)|(spec\|)|(hconcat\|)|(vconcat\|)|(layer\|)", "", p_key)
                            if p_key not in vegalite_definition_dict:
                                vegalite_definition_dict[p_key] = []
                            vegalite_definition_dict[p_key].append(value)

                        # accumulate all vegalite definition with universal format
                        func_dict = OrderedDict()
                        for key, value in vegalite_definition_dict.items():
                            seqs = key.rsplit("|", maxsplit=1)
                            if len(seqs) == 1:
                                func_name, arg = seqs[0], seqs[0]
                            elif len(seqs) == 2:
                                func_name, arg = seqs[0], seqs[1]
                            else:
                                raise ValueError("Invalid key!")
                            if func_name not in func_dict:
                                func_dict[func_name] = defaultdict(list)
                            
                            # retrieve default value
                            for v in value:
                                func_dict[func_name][arg].append(v)

                        for func_name, arg_dict in func_dict.items():
                            output_json_obj = {
                                "var_call": "None", 
                                "func_name": func_name, 
                                "args": [], 
                                "kargs": arg_dict, 
                                "target_lib": "vega-lite"
                            }
                            universal_items.append(output_json_obj)
                    
                    if len(universal_items) > 0:
                        fo.write(json.dumps({
                            "file_id": hexsha,
                            "content": universal_items
                        }, ensure_ascii=False) + "\n")
                except:
                    print("Error")
    fo.close()


if __name__ == "__main__":
    # jsonl_file_path, obtained from "../download_thestack.py"
    jsonl_file_path = "data/raw-data/the-stack/JSON.vega-lite.jsonl"
    output_file_path = "data/universal/Vegalite_Vega.universal2.jsonl"
    
    main_vegalite_parsing_from_the_stack(jsonl_file_path, output_file_path)
                    

                


