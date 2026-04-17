import glob
import json
import os
import nbformat
from collections import defaultdict
from tqdm import tqdm
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def extract_lib(line):
    line = line.strip()
    if line.startswith("import ") or line.startswith("from "):
        # Extract the library name from the import statement
        if "import" in line:
            return line.split()[1].split(".")[0]
        elif "from" in line:
            return line.split()[1]
    return None


def calculate_freq():
    lib_frequency = defaultdict(int)
    
    dataset = "GitHub"
    if dataset == "REDCap":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/Version_1/round_*/*/annotations/t2v_notebook_true/*.ipynb"
        nb_paths = glob.glob(glob_path)
    elif dataset == "GitHub":
        glob_path = "/Users/nngu0448/Documents/data/github-data/Batch-*/*/*/t2v_notebook_true/*.ipynb"
        nb_paths = glob.glob(glob_path)


    nb_paths = sorted(nb_paths)
    for nb_path in tqdm(nb_paths):
        assert os.path.exists(nb_path), f"Notebook path {nb_path} does not exist."
        
        nb = nbformat.read(nb_path, as_version=4)
        lib_set = set()
        for cell in nb.cells:
            if cell.cell_type == "code":
                lines = cell.source.split("\n")
                for line in lines:
                    lib_name = extract_lib(line)
                    if lib_name:
                        lib_set.add(lib_name.strip().strip(",.;"))
                        
        for lib_name in lib_set:
            lib_frequency[lib_name] += 1

    # sort the libraries by frequency
    lib_frequency = sorted(lib_frequency.items(), key=lambda x: x[1], reverse=True)
    
    # write to csv file
    output_path = f"data/analysis-result-p2/library-usage/{dataset}_library-usage-freq.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Library,Frequency\n")
        for lib, freq in lib_frequency:
            f.write(f"{lib},{freq}\n")

def main_analysis_library_usage():
    github_path = "data/p2-analysis1/distinct_library/GitHub-T2V_library-freq.csv"
    arxiv_path = "data/p2-analysis1/distinct_library/arXiv-T2V_library-freq.csv"
    
    # load the data and make bar chart
    github_df = pd.read_csv(github_path)
    arxiv_df = pd.read_csv(arxiv_path)
    
    # add new column for dataset
    github_df["Dataset"] = "GitHub-T2V"
    arxiv_df["Dataset"] = "arXiv-T2V"
    
    # concatenate the dataframes
    combined_df = pd.concat([github_df, arxiv_df], ignore_index=True)
    
    # get top 10 libraries for each dataset
    top_github = github_df.nlargest(10, "Frequency")
    top_arxiv = arxiv_df.nlargest(10, "Frequency")

    
    # merge the top libraries
    top_combined = pd.concat([top_github, top_arxiv], ignore_index=True)

    # plot the data using seaborn (vertical bar chart)
    plt.figure(figsize=(4, 4))
    sns.barplot(data=top_combined, y="Library", x="Frequency", hue="Dataset")
    # plt.title("Top 10 Libraries Used in GitHub and arxiv Notebooks")
    plt.legend(title="Dataset", fontsize=10, title_fontsize=12)
    plt.xticks(rotation=0, ha="right", fontsize=12)
    # set y-ticks to be larger
    plt.yticks(fontsize=12)
    # remove the y-axis label
    plt.xlabel("Frequency", fontsize=12)
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("data/p2-analysis1/distinct_library/analysis-top-libraries.pdf", dpi=300)
    plt.show()

def extract_distinct_libraries_nb(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    lib_set = set()
    for cell in nb.cells:
        if cell.cell_type == "code":
            lines = cell.source.split("\n")
            for line in lines:
                lib_name = extract_lib(line)
                if lib_name:
                    lib_set.add(lib_name.strip().strip(",.;"))
    return lib_set

def extract_distinct_libraries_py(py_path):
    lib_set = set()
    with open(py_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
            lib_name = extract_lib(line)
            if lib_name:
                lib_set.add(lib_name.strip().strip(",.;"))
    return lib_set

if __name__ == "__main__":
    main_analysis_library_usage()
    
    # dataset = "arXiv-T2V"
    
    # if dataset == "ChartX":
    #     glob_path = "/Users/nngu0448/Documents/data/ChartX-Dataset/my_parsing/*/*/notebook.ipynb"
    #     nb_paths = glob.glob(glob_path)
    # elif dataset == "Text2Chart31":
    #     glob_path = "/Users/nngu0448/Documents/data/Text2Chart31-Dataset/Text2Chart31-test/*/t2v_notebook_true/*.ipynb"
    #     nb_paths = glob.glob(glob_path)
    # elif dataset == "GitHub-T2V":
    #     glob_path = "/Users/nngu0448/Documents/data/github-data/github-v2/test*/t2v_gt/test*.py"
    #     nb_paths = glob.glob(glob_path)
    # elif dataset == "arXiv-T2V":
    #     glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/arxiv-v3/r*/t2v_gt/r*.py"
    #     glob_path_2 = "/Users/nngu0448/Documents/data/REDCap-VisReflect/arxiv-v32/r*/t2v_gt/r*.py"
    #     nb_paths = glob.glob(glob_path)
    #     nb_paths += glob.glob(glob_path_2)
        
        
    # print(f"Total number of notebooks: {len(nb_paths)}")
    # counter = []
    # lib_frequency = defaultdict(int)
    # stats_data = []
    # nb_paths = sorted(nb_paths)
    # for nb_path in tqdm(nb_paths):

    #     if nb_path.endswith(".ipynb"):
    #         lib_set = extract_distinct_libraries_nb(nb_path)
    #     elif nb_path.endswith(".py"):
    #         lib_set = extract_distinct_libraries_py(nb_path)
    #     elif nb_path.endswith(".vis-request.txt"):
    #         py_path = nb_path.replace(".vis-request.txt", ".py")
    #         lib_set = extract_distinct_libraries_py(py_path)
    #     else:
    #         raise ValueError(f"Unsupported file type: {nb_path}")
        
    #     if "warnings" in lib_set:
    #         lib_set.remove("warnings")
    #     if "t2vlog" in lib_set:
    #         lib_set.remove("t2vlog")
        
    #     stats_data.append({
    #         "notebook_path": nb_path,
    #         "# distinct libraries": len(lib_set),
    #         "libraries": list(lib_set)
    #     })
    #     for lib_name in lib_set:
    #         lib_frequency[lib_name] += 1
    #     counter.append(len(lib_set))
    
    # df = pd.DataFrame(stats_data)
    
    # # add a new row for average
    # avg_row = {
    #     "notebook_path": "Average",
    #     "# distinct libraries": df["# distinct libraries"].mean(),
    #     "libraries": ""
    # }
    # df = df._append(avg_row, ignore_index=True)
    
    # # save the stats data for each file
    # output_path = f"data/p2-analysis1/distinct_library/{dataset}_library-set.csv"
    # os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # df.to_csv(output_path, index=False, encoding="utf-8")
    
    # # save the library frequency
    # lib_frequency = sorted(lib_frequency.items(), key=lambda x: x[1], reverse=True)
    
    # # write to csv file
    # output_path = f"data/p2-analysis1/distinct_library/{dataset}_library-freq.csv"
    # os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # with open(output_path, "w", encoding="utf-8") as f:
    #     f.write("Library,Frequency\n")
    #     for lib, freq in lib_frequency:
    #         f.write(f"{lib},{freq}\n")