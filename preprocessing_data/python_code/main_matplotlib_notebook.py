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
    # main_matplotlib_notebook()
    
    target_lib = "matplotlib"
    
    if target_lib == "matplotlib":
        matplotlib_schema_dir = "/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/raw-data/schema/matplotlib_schema"
        schema_dict = load_matplotlib_schema(matplotlib_schema_dir=matplotlib_schema_dir,
                                                        library_name="matplotlib",
                                                        version_list=["3.8.1", "2.2.5" ,"1.5.3"])
    elif target_lib == "pandas":
        pandas_schema_dir = "/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/raw-data/schema/pandas_schema"
        schema_dict = load_matplotlib_schema(matplotlib_schema_dir=pandas_schema_dir,
                                                    library_name="pandas",
                                                    version_list=["2.2.3"])
    elif target_lib == "seaborn":
        seaborn_schema_dir = "/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/raw-data/schema/seaborn_schema"
        schema_dict = load_matplotlib_schema(matplotlib_schema_dir=seaborn_schema_dir,
                                                library_name="seaborn",
                                                version_list=["0.13.2"])
    else:
        raise ValueError(f"Unsupported target library: {target_lib}")
    
    
    import glob
    dataset = "REDCap"
    if dataset == "Github":
        glob_path = "/Users/nngu0448/Documents/data/github-data/*/*/*/*_t2v_detection.json"
        nb_detection_paths = sorted(glob.glob(glob_path))
        nb_paths = [path.replace("_t2v_detection.json", ".ipynb") for path in nb_detection_paths]
        
    elif dataset == "REDCap":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/Version_1/round_*/*/annotations/annotation.ipynb"
        nb_paths = sorted(glob.glob(glob_path))
    
    data = []

    for nb_path in nb_paths:
        assert os.path.exists(nb_path), f"{nb_path} does not exist"
        
        # nb_path = '/Users/nngu0448/Documents/data/github-data/Batch-1/test-set-plotcoder/plotcoder_0001/Exercises_code_with_solutions.ipynb'
        notebook = nbformat.read(nb_path, as_version=4)

        # filter and preprocess code cells
        code_cells = []
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                code_cells.append(filter_by_lines(cell.source))

        universal_items = []
        universal_items = parse_ast_for_notebook_cells(schema_dict, code_cells, target_lib=target_lib)
        
        print(f"Processing {nb_path}")
        print(len(universal_items))
        for item in universal_items:
            print(item)
        print("=====================================")
        
        data.append({
            "file_path": nb_path,
            "content": universal_items
        })

    output_path = f"/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/universal_phase2/{dataset}.notebook.{target_lib}.universal2.jsonl"
    with open(output_path, "w") as fo:
        for item in data:
            fo.write(json.dumps(item, ensure_ascii=False) + "\n")
            

    


            