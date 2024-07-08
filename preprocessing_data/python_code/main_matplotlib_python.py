import ast
import os
from tqdm import tqdm
import json
from utils import get_file_length
from utils_ast import rev_extract_all_command
from parse_ast_tree import handle_node
from matplotlib_schema_parsing import load_matplotlib_schema
from convert_to_universal import convert_to_universal_format


def post_process_parsed_nodes(matplotlib_schema_dict, parsed_nodes, verbose=False):
    result = []
    for node in parsed_nodes:
        try:
            json.dumps(node)
            if "target" in node:
                node.pop("target")
            universal_node = convert_to_universal_format(node, matplotlib_schema_dict, verbose=verbose)
            result.append(universal_node)
        except:
            continue
    return result

def main_extract_call_func():
    # Load matplotlib schema - already prepared in "data/raw-data/schema/matplotlib_schema"
    # You can obtain the schema by running "python ./matplotlib_schema_parsing.py"
    matplotlib_schema_dir = "data/raw-data/schema/matplotlib_schema"
    matplotlib_schema_dict = load_matplotlib_schema(matplotlib_schema_dir=matplotlib_schema_dir, 
                                                    version_list=["3.8.1", "2.2.5" ,"1.5.3"])
    
    # jsonl_file_path, obtained from "../download_thestack.py"
    jsonl_file_path = "data/raw-data/the-stack/Python.matplotlib.jsonl"
    output_file_path = "data/universal/Matplotlib_Python.universal2.jsonl"
    
    assert os.path.exists(jsonl_file_path), f"{jsonl_file_path} does not exist"
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    fo = open(output_file_path, mode="w", encoding="utf-8")

    num_lines = get_file_length(jsonl_file_path)
    with open(jsonl_file_path, mode="r", encoding="utf-8") as fi:
        for line in tqdm(fi, total=num_lines):
            if line.strip() != "":
                json_data = json.loads(line.strip())
                hexsha = json_data["hexsha"]
                try:
                    # AST parsing
                    tree = ast.parse(source=json_data["content"])
                    # Extract all command
                    nodes = rev_extract_all_command(tree)
                    variable_list = []
                    content = []
                    for node in nodes:
                        # Parse function command and convert to universal format
                        parsed_nodes, variable_list = handle_node(node, 
                                    target_lib="matplotlib", 
                                    variable_list=variable_list, 
                                    verbose=False)
                        content += post_process_parsed_nodes(matplotlib_schema_dict, parsed_nodes, verbose=False)
                    if len(content) > 0:
                        fo.write(json.dumps({"file_id": hexsha, "content": content})+"\n")
                except KeyboardInterrupt:
                    break
                except:
                    continue

    fo.close()


if __name__ == "__main__":
    main_extract_call_func()
    

    

    


        
        

        