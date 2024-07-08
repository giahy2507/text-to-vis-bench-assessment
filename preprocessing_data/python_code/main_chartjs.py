import os
import json
import pickle
import re
from tqdm import tqdm
import glob
from pprint import pprint
import re
from collections import defaultdict, OrderedDict
from utils_ast_JS import recursive_extract_obj_expression, transform_node_to_json
from utils_ast_JS import check_chartjs_in_code, check_json_line_in_schema_table
from utils import flatten_json


def extract_chartjs_json_in_ast_json(thestack_output_dir, 
                                     schema_tables):

    input_glob = f"{thestack_output_dir}/*.js.ast.json"
    paths = sorted(glob.glob(input_glob))
    for path in tqdm(paths):
        print(os.path.basename(path))
        assert os.path.isfile(path)
        filtered_data = []
        
        # load json ast tree of Javascript code
        data = json.load(open(path, mode="r", encoding="utf-8"))

        # parse asr tree to extract all object expression
        result = recursive_extract_obj_expression(data)
        results_jsonl = []
        for item in result:
            # simplify the object expression to json object with key, value
            data = transform_node_to_json(item)
            results_jsonl.append(json.dumps(data)) 
        
        # check if there are "type", "data", "options" in the json object --> chartjs
        checking = check_chartjs_in_code(results_jsonl)
        if checking:
            for line in results_jsonl:
                if check_chartjs_in_code([line]):
                    # easily extraction for basic items: "type", "data", "options"
                    filtered_data.append(line)
                else:
                    # extraction for non basic items
                    if check_json_line_in_schema_table(schema_tables, line, threshold=3, verbose=False):
                        # check if the json object is in the schema tables (definition of functions in chartjs)
                        filtered_data.append(line)

        output_path = path.replace(".js.ast.json", ".chartjs.jsonl")
        with open(output_path, mode="w", encoding="utf-8") as f:
            f.write("\n".join(filtered_data))


def check_chartjs_basic_items(json_data):
    if "type" in json_data and "options" in json_data and "data" in json_data:
        return True
    else:
        return False
    

def check_non_basic_item(basic_items_dict, non_basic_key):
    non_basic_key_seqs = non_basic_key.split("|")
    if len(non_basic_key_seqs) <= 1:
        return None
    else:
        for key in basic_items_dict.keys():
            basic_key_seqs = key.split("|")
            if len(basic_key_seqs) <= 1:
                continue
            if non_basic_key_seqs[-1] == basic_key_seqs[-1]:
                basic_namespace_seqs = set(basic_key_seqs[:-1])
                nbasic_namespace_seqs = set(non_basic_key_seqs[:-1])
                if len(basic_namespace_seqs & nbasic_namespace_seqs) == len(nbasic_namespace_seqs):
                    return key
        return None


def get_chartjs_flatten_JSON_data(filtered_data_lines):
    basic_items = []
    non_basic_items = []
    # categorize by chartjs basic items: "type", "options", "data"
    for line in filtered_data_lines:
        if line.strip() != "":
            json_data = json.loads(line.strip())
            if check_chartjs_basic_items(json_data):
                basic_items.append(json_data)
            else:
                non_basic_items.append(json_data)

    # flatten all data
    basic_items_dict = defaultdict(list)
    for json_data in basic_items:
        json_flat = flatten_json(json_data)
        for key, value in json_flat:
            p_key = re.sub(r'\[\d+\]', '', key)
            basic_items_dict[p_key].append(value)
    non_basic_items_dict = defaultdict(list)
    for json_data in non_basic_items:
        json_flat = flatten_json(json_data)
        for key, value in json_flat:
            p_key = re.sub(r'\[\d+\]', '', key)
            non_basic_items_dict[p_key].append(value)

    # use key in non_basic_items_dict to check key in basic_items_dict
    for key, value in non_basic_items_dict.items():
        detected_key = check_non_basic_item(basic_items_dict, key)
        if detected_key:
            basic_items_dict[detected_key].append(value)

    return basic_items_dict


def identify_the_best_schema_table(schema_tables, key_name, verbose=False):
    scores = [0] * len(schema_tables)
    key_name_seqs = key_name.split("|")
    if len(key_name_seqs) <= 1:
        return None
        
    namespace_seqs = key_name_seqs[:-1]
    for i, schema_table in enumerate(schema_tables):
        # reward for key_name
        if key_name_seqs[-1] not in schema_table["table"]:
            scores[i] = -999999999
            continue
        
        # reward for namespace
        if len(schema_table["namespaces_p"]):
            name_space_score = [0]*len(schema_table["namespaces_p"])
            for j, namespace in enumerate(schema_table["namespaces_p"]):
                name_space_score[j] = len(set(namespace_seqs) & set(namespace)) * 0.5
            scores[i] += max(name_space_score)

        # reward for chartjs version
        if schema_table["chartjs-version"] == "4.4.0":
            scores[i] += 0.1
    
    if max(scores) > 1:
        max_score_idx = scores.index(max(scores))
        return schema_tables[max_score_idx]
    else:
        return None
    

def get_lines_of_file(file_path):
    lines = []
    with open(file_path, mode="r", encoding="utf-8") as f:
        for line in f:
            if line.strip() != "":
                lines.append(line.strip())
    return lines


if __name__ == "__main__":
    thestack_output_dir = "data/raw-data/the-stack/JavaScript_ChartJS"
    universal_output_path = "data/universal/ChartJS_JavaScript.universal2.jsonl"
    
    chartjs_schema_table = "data/raw-data/schema/graphics_schema/schema_tables.json"
    schema_tables = json.load(open(chartjs_schema_table, mode="r", encoding="utf-8"))

    # Detect and extract ChartJS code from AST JSON
    extract_chartjs_json_in_ast_json(thestack_output_dir=thestack_output_dir, 
                                     schema_tables=schema_tables)

    # Get all chartjs jsonl files to get foundation items
    chartjs_glob_path = f"{thestack_output_dir}/*.chartjs.jsonl"
    chartjs_paths = sorted(glob.glob(chartjs_glob_path))
    all_lines = []
    for chartjs_path in chartjs_paths:
        all_lines += get_lines_of_file(chartjs_path)
    all_basic_items_dict = get_chartjs_flatten_JSON_data(all_lines)
    
    # Output Universal-v2 formats
    fo = open(universal_output_path, mode="w", encoding="utf-8")

    for chartjs_path in chartjs_paths:
        lines = get_lines_of_file(chartjs_path)

        file_id = os.path.basename(chartjs_path).replace(".chartjs.jsonl", "")
        content = []
        for line in lines:
            basic_items_dict = get_chartjs_flatten_JSON_data([line])
            
            func_dict = OrderedDict()
            for key, value in basic_items_dict.items():
                seqs = key.rsplit("|", maxsplit=1)
                if len(seqs) == 1:
                    func_name, arg = seqs[0], seqs[0]
                elif len(seqs) == 2:
                    func_name, arg = seqs[0], seqs[1]
                else:
                    raise ValueError("Invalid key!")
                
                if func_name not in func_dict:
                    func_dict[func_name] = defaultdict(list)

                if key in all_basic_items_dict:
                    schema_table = identify_the_best_schema_table(schema_tables, key, verbose=False)
                    default_value = "undefined"
                    if schema_table:
                        default_value = schema_table["table"][key.split("|")[-1]]

                    for v in value:
                        # # Universal Version 1, containing default value for each argument
                        # func_dict[func_name][arg].append((v, default_value))

                        # Universal Version 2, containing only value
                        func_dict[func_name][arg].append(v)

            for func_name, arg_dict in func_dict.items():
                content.append({
                    "var_call": "None", 
                    "func_name": func_name, 
                    "args": [], 
                    "kargs": arg_dict, 
                    "target_lib": "chartjs"
                })

        fo.write(json.dumps({
            "file_id": file_id, 
            "content": content
        })+"\n")

    fo.close()