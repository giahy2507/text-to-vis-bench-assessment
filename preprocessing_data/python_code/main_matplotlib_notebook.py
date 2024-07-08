import nbformat
import json
import os
from tqdm import tqdm
from utils_notebook import parse_ast_for_notebook_cells, filter_by_lines
from matplotlib_schema_parsing import load_matplotlib_schema
from utils import get_file_length



# use nbformat to extract all code cell of the notebook path
def extract_code_cells(notebook_path):
    with open(notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)
        code_cells = []
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                code_cells.append(cell.source)
    return code_cells


def main_matplotlib_notebook():
    # Load matplotlib schema - already prepared in "data/raw-data/schema/matplotlib_schema"
    # You can obtain the schema by running "python ./matplotlib_schema_parsing.py"
    matplotlib_schema_dir = "data/raw-data/schema/matplotlib_schema"
    matplotlib_schema_dict = load_matplotlib_schema(matplotlib_schema_dir=matplotlib_schema_dir, 
                                                    version_list=["3.8.1", "2.2.5" ,"1.5.3"])

    # jsonl_file_path, obtained from "../download_thestack.py"
    jsonl_file_path = "data/raw-data/the-stack/Jupyter_Notebook.matplotlib.jsonl"
    output_file_path = "data/universal/Matplotlib_Notebook.universal2.jsonl"
    assert os.path.exists(jsonl_file_path), f"{jsonl_file_path} does not exist"
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    fo = open(output_file_path, mode="w", encoding="utf-8")

    length = get_file_length(jsonl_file_path)
    with open(jsonl_file_path, mode="r", encoding="utf-8") as fi:
        for line in tqdm(fi, total=length):
            try:
                nb_data = json.loads(line)
                content = json.loads(nb_data["content"])
                file_id = nb_data["hexsha"]

                notebook = nbformat.reads(nb_data["content"], as_version=content["nbformat"])

                # filter and preprocess code cells
                code_cells = []
                for cell in notebook.cells:
                    if cell.cell_type == 'code':
                        code_cells.append(filter_by_lines(cell.source))

                universal_items = []
                universal_items = parse_ast_for_notebook_cells(matplotlib_schema_dict, code_cells)
                if len(universal_items) > 0:
                    fo.write(json.dumps({
                        "file_id": file_id,
                        "content": universal_items
                    }, ensure_ascii=False) + "\n")
            except Exception as e:
                # print(e)
                continue

    fo.close()


if __name__ == "__main__":
    main_matplotlib_notebook()

    # jsonl_path = "/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-2/Matplotlib_Python/Matplotlib_Python.universal2.jsonl"


    # total_function = 0
    # with open(jsonl_path, mode="r", encoding="utf-8") as fi:
    #     for line in fi:
    #         json_data = json.loads(line)
    #         content = json_data["content"]
    #         total_function += len(content)
    
    # print(total_function)
            

    


            