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

if __name__ == "__main__":
    github_path = "data/analysis-result-p2/library-usage/GitHub_library-usage-freq.csv"
    redcap_path = "data/analysis-result-p2/library-usage/REDCap_library-usage-freq.csv"
    
    # load the data and make bar chart
    github_df = pd.read_csv(github_path)
    redcap_df = pd.read_csv(redcap_path)
    
    # add new column for dataset
    github_df["Dataset"] = "DA-T2V"
    redcap_df["Dataset"] = "arXiv-T2V"
    
    # concatenate the dataframes
    combined_df = pd.concat([github_df, redcap_df], ignore_index=True)
    
    # get top 10 libraries for each dataset
    top_github = github_df.nlargest(10, "Frequency")
    top_redcap = redcap_df.nlargest(10, "Frequency")

    
    # merge the top libraries
    top_combined = pd.concat([top_github, top_redcap], ignore_index=True)

    # plot the data using seaborn (vertical bar chart)
    plt.figure(figsize=(6, 4))
    sns.barplot(data=top_combined, y="Library", x="Frequency", hue="Dataset")
    # plt.title("Top 10 Libraries Used in GitHub and REDCap Notebooks")
    plt.legend(title="Dataset", fontsize=10, title_fontsize=12)
    plt.xticks(rotation=0, ha="right", fontsize=12)
    # set y-ticks to be larger
    plt.yticks(fontsize=12)
    # remove the y-axis label
    plt.xlabel("Frequency", fontsize=12)
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig("data/analysis-result-p2/library-usage/analysis-top-libraries.pdf", dpi=300)
    plt.show()
