import nbformat
import json
import os
from tqdm import tqdm
from utils_notebook import parse_ast_for_notebook_cells, filter_by_lines
from matplotlib_schema_parsing import load_matplotlib_schema
from utils import get_file_length
import glob
    



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

# loading schema for matplotlib, pandas, seaborn
matplotlib_schema_dir = "/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/raw-data/schema/matplotlib_schema"
schema_matplotlib_dict = load_matplotlib_schema(matplotlib_schema_dir=matplotlib_schema_dir,
                                                library_name="matplotlib",
                                                version_list=["3.8.1", "2.2.5" ,"1.5.3"])
pandas_schema_dir = "/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/raw-data/schema/pandas_schema"
schema_pandas_dict = load_matplotlib_schema(matplotlib_schema_dir=pandas_schema_dir,
                                            library_name="pandas",
                                            version_list=["2.2.3"])
seaborn_schema_dir = "/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/raw-data/schema/seaborn_schema"
schema_seaborn_dict = load_matplotlib_schema(matplotlib_schema_dir=seaborn_schema_dir,
                                        library_name="seaborn",
                                        version_list=["0.13.2"])
plotly_schema_dir = "/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/raw-data/schema/plotly.py_schema"
schema_plotly_dict = load_matplotlib_schema(matplotlib_schema_dir=plotly_schema_dir,
                                            library_name="plotly.py",
                                            version_list=["6.2.0"])
lib_schema = {
    "matplotlib": schema_matplotlib_dict,
    "pandas": schema_pandas_dict,
    "seaborn": schema_seaborn_dict,
    "plotly": schema_plotly_dict
}

def main_vislib_notebook(dataset):
    if dataset == "GitHub-T2V":
        glob_path = "/Users/nngu0448/Documents/data/github-data/github-v2/test*/t2v_gt/test*.py"
        nb_paths = sorted(glob.glob(glob_path))
        
    elif dataset == "arXiv-T2V":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/arxiv-v3/r*/t2v_gt/r*.py"
        nb_paths = sorted(glob.glob(glob_path))
        glob_path_2 = "/Users/nngu0448/Documents/data/REDCap-VisReflect/arxiv-v32/r*/t2v_gt/r*.py"
        nb_paths += sorted(glob.glob(glob_path_2))
        
    elif dataset == "ChartX":
        glob_path = "/Users/nngu0448/Documents/data/ChartX-Dataset/my_parsing/*/*/notebook.ipynb"
        nb_paths = sorted(glob.glob(glob_path))
        
    elif dataset == "Text2Chart31":
        glob_path = "/Users/nngu0448/Documents/data/Text2Chart31-Dataset/Text2Chart31-test/*/t2v_notebook_true/*.ipynb"
        nb_paths = sorted(glob.glob(glob_path))
    
    elif dataset == "test":
        glob_path = "/Users/nngu0448/Documents/data/ChartX-Dataset/my_parsing/test/sample-00917-funnel-163/notebook.ipynb"
        nb_paths = sorted(glob.glob(glob_path))
    
    else:
        raise ValueError(f"Unknown dataset: {dataset}")

    data = []

    for nb_path in tqdm(nb_paths):
        assert os.path.exists(nb_path), f"{nb_path} does not exist"
        
        code_cells = []
        if nb_path.endswith(".ipynb"):
            notebook = nbformat.read(nb_path, as_version=4)
            
            # filter and preprocess code cells
            for cell in notebook.cells:
                if cell.cell_type == 'code':
                    code_cells.append(filter_by_lines(cell.source))
        elif nb_path.endswith(".py"):
            code_content = open(nb_path, mode="r", encoding="utf-8").read()
            code_cells = [code_content]
        
        universal_items = []
        for target_lib, schema_dict in lib_schema.items():
            if schema_dict is None:
                continue
            universal_items.extend(parse_ast_for_notebook_cells(schema_dict, code_cells, target_lib=target_lib))
        
        print(f"Processing {nb_path}")
        print(len(universal_items))
        for item in universal_items:
            print(item)
        print("=====================================")
        
        data.append({
            "file_path": nb_path,
            "content": universal_items
        })

    output_path = f"/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/universal_phase2/Matplotlib_{dataset}.notebook.4-vis-libs.universal2.jsonl"
    with open(output_path, "w") as fo:
        for item in data:
            fo.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print("-"*100)

if __name__ == "__main__":
    # main_matplotlib_notebook()
    # main_vislib_notebook("GitHub-T2V")
    main_vislib_notebook("arXiv-T2V")
    
    # main_vislib_notebook("ChartX")
    # main_vislib_notebook("Text2Chart31")
    
    
            

    


            