import glob
import json
import os
import nbformat
from collections import defaultdict
from tqdm import tqdm


def extract_lib(line):
    line = line.strip()
    if line.startswith("import ") or line.startswith("from "):
        # Extract the library name from the import statement
        if "import" in line:
            return line.split()[1].split(".")[0]
        elif "from" in line:
            return line.split()[1]
    return None

if __name__ == "__main__":
    
    lib_frequency = defaultdict(int)
    
    dataset = "REDCap"
    
    if dataset == "REDCap":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/Round2/Email/a_valid/*/annotations/annotation.ipynb"
        nb_paths = glob.glob(glob_path)
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/Round1/2025-02-17-1157/annotated_py/*/annotations/annotation.ipynb"
        nb_paths += glob.glob(glob_path)
        
    elif dataset == "GitHub Notebooks":
        glob_path = "/Users/nngu0448/Documents/data/github-data/Batch-*/*/*/*_t2v_detection.json"
        paths = glob.glob(glob_path)
        nb_paths = [path.replace("_t2v_detection.json", ".ipynb") for path in paths]


    nb_paths = sorted(nb_paths)
    for nb_path in tqdm(nb_paths):
        assert os.path.exists(nb_path), f"Notebook path {nb_path} does not exist."
        
        nb = nbformat.read(nb_path, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == "code":
                lines = cell.source.split("\n")
                for line in lines:
                    lib_name = extract_lib(line)
                    if lib_name:
                        lib_frequency[lib_name.strip().strip(",.;")] += 1
    
    # sort the libraries by frequency
    lib_frequency = sorted(lib_frequency.items(), key=lambda x: x[1], reverse=True)
    
    # write to csv file
    output_path = "library_usage_frequency_redcap.csv"
    with open(output_path, "w", encoding="utf-8") as f: 
        f.write("Library,Frequency\n")
        for lib, freq in lib_frequency:
            f.write(f"{lib},{freq}\n")
                        
                        
        
        
