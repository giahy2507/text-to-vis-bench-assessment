import glob
import json
import os
from altair import value
import nbformat
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


plot_type_map = {
    "plot": "line",
    "axhline": "line",
    "axvline": "line",
    "stem": "line",
    "errorbar": "line",
    "step": "line",

    "scatter": "scatter",
    "scatter3d": "scatter",
    
    "hist": "bar",
    "bar": "bar",
    "barh": "bar",
    "bar3d": "bar",

    "bxp": "box",
    
    "fill_between": "area",
    "fill_betweenx": "area",
    
    "pie": "pie",
    
    "contour": "contour",
    "contourf": "contour",
    
    "pcolormesh": "heatmap",
    "imshow": "heatmap",
    "hexbin": "heatmap",
    "hist2d": "heatmap",
    "plot_surface3d": "heatmap",
}

def main_calculate_plot_type_freq(dataset="Github"):
    
    if dataset == "Github":
        glob_path = "/Users/nngu0448/Documents/data/github-data/Version_1/*/*/t2v_notebook_true/*_log"
    elif dataset == "REDCap":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/Version_1/round_*/*/annotations/t2v_notebook_true/*_log"
    else:
        raise ValueError("Unknown dataset")
    log_dirs = sorted(glob.glob(glob_path))
    
    # Prepare data for analysis
    plt_func_freq = defaultdict(set)
    unknown_plot_types = defaultdict(int)
    for log_dir in tqdm(log_dirs):
        plt_func_set = set()
        json_paths = sorted(glob.glob(os.path.join(log_dir, "*.json")))
        for json_path in json_paths:
            if "variables.json" in json_path:
                continue
            json_data = json.load(open(json_path, "r", encoding="utf-8"))
            plt_func = json_data.get("plt_func", "")
            if plt_func in plot_type_map:
                plt_func_mapped = plot_type_map[plt_func]
                plt_func_set.add(plt_func_mapped)
            else:
                unknown_plot_types[plt_func] += 1
        plt_func_freq[log_dir] = plt_func_set
        

    # Analysis of plot types with their frequency - global
    plt_func_global_freq = defaultdict(int)
    for plt_func_set in plt_func_freq.values():
        for plt_func in plt_func_set:
            plt_func_global_freq[plt_func] += 1
    plt_func_global_freq = sorted(plt_func_global_freq.items(), key=lambda x: x[1], reverse=True)
    
    # write to csv file
    output_path = f"data/analysis-result-p2/plot-type/{dataset}-plottype-global-freq.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Plot Type,Frequency\n")
        for plt_func, freq in plt_func_global_freq:
            f.write(f"{plt_func},{freq}\n")
            
    # plot
    plt.figure(figsize=(10, 6))
    plt.bar([x[0] for x in plt_func_global_freq], [x[1] for x in plt_func_global_freq], color='skyblue')
    plt.xlabel('Plot Type')
    plt.ylabel('Frequency')
    plt.title('Frequency of Plot Types')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path.replace(".csv", ".png"))
    
    
    # -----------------
    # Analysis of the distribution of the number of distinct plot types per log directory
    freq_per_log = defaultdict(int)
    for log_dir, plt_func_set in plt_func_freq.items():
        freq_per_log[len(plt_func_set)] += 1
        if len(plt_func_set) == 0:
            print(log_dir)
            
    # count average plt func per log_dir
    plt_func_avg_per_log = {log_dir: len(plt_func_set) for log_dir, plt_func_set in plt_func_freq.items()}
    plt_func_avg = sum(plt_func_avg_per_log.values()) / len(plt_func_avg_per_log)
            
    # write to csv file
    output_path = f"data/analysis-result-p2/plot-type/{dataset}-number-of-distinct-plottype-freq.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("Number of Distinct Plot Types,Frequency\n")
        for num_types, freq in freq_per_log.items():
            f.write(f"{num_types},{freq}\n")
        
    plt.figure(figsize=(10, 6))
    plt.bar(freq_per_log.keys(), freq_per_log.values(), color='lightgreen')
    plt.xlabel('Number of Distinct Plot Types')
    plt.ylabel('Frequency of Log Directories')
    plt.title('Frequency of Log Directories by Number of Distinct Plot Types. Average: {:.2f}'.format(plt_func_avg))
    plt.xticks(list(freq_per_log.keys()), rotation=45)
    plt.tight_layout()
    plt.savefig(output_path.replace(".csv", ".png"))
    
    print("-" * 50)
    print("Frequency of unknown plot types:")
    for plt_func, freq in unknown_plot_types.items():
        print(f"  {plt_func}: {freq}")

def main_visualise_plot_type_freq():
    # main_calculate_plot_type_freq(dataset="Github")
    # main_calculate_plot_type_freq(dataset="REDCap")
    github_path = "data/analysis-result-p2/plot-type/Github-plottype-global-freq.csv"
    redcap_path = "data/analysis-result-p2/plot-type/REDCap-plottype-global-freq.csv"
    
    # load the data using pandas
    github_df = pd.read_csv(github_path)
    redcap_df = pd.read_csv(redcap_path)
    
    # add new column for dataset
    github_df["Dataset"] = "DA-T2V"
    redcap_df["Dataset"] = "arXiv-T2V"
    
    # concatenate the dataframes
    combined_df = pd.concat([github_df, redcap_df], ignore_index=True)
    
    # plot using seaborn
    plt.figure(figsize=(6, 4))
    sns.barplot(data=combined_df, x="Frequency", y="Plot Type", hue="Dataset", palette="viridis")
    # plt.title("Frequency of Plot Types in GitHub and REDCap Notebooks")
    plt.xlabel("Frequency", fontsize=12)
    plt.ylabel("", fontsize=12)
    plt.legend(title="Dataset", fontsize=10, title_fontsize=12)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig("data/analysis-result-p2/plot-type/analysis-plottypes.pdf", dpi=300)
    plt.show()


if __name__ == "__main__":
    tsv_path = "/Users/nngu0448/Documents/usyd/projects/text-to-vis-benchmarks-assessment/data/p2-analysis2/comparison-plottype.tsv"
    
    df = pd.read_csv(tsv_path, sep='\t')
    
    print(df.head())
    
    # tranform to long format
    nb_matplotlib_column = df["nb-Matplotlib"].tolist()
    DA_t2v_column = df["DA-T2V"].tolist()
    arxiv_t2v_column = df["arXiv-T2V"].tolist()
    plottype_values = df["Chart Type"].tolist()
    
    # create a new dataframe {x: plottype, y: frequency, dataset: dataset_name}
    data = []
    for i in range(len(plottype_values)):
        data.append({"Plot Type": plottype_values[i], 
                     "Frequency": nb_matplotlib_column[i], 
                     "Dataset": "Matplotlib-nb"})
        data.append({"Plot Type": plottype_values[i], 
                     "Frequency": DA_t2v_column[i], 
                     "Dataset": "DA-T2V"})
        data.append({"Plot Type": plottype_values[i], 
                     "Frequency": arxiv_t2v_column[i], 
                     "Dataset": "arXiv-T2V"})
    new_df = pd.DataFrame(data)
    
    # plot using seaborn
    plt.figure(figsize=(6, 4))
    sns.barplot(data=new_df, y="Frequency", x="Dataset", hue="Plot Type")
    plt.xlabel("")
    plt.ylabel("Percentage", fontsize=14)
    # legened with background color transparent with alpha=0.5
    plt.legend(fontsize=10, framealpha=0.5)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    
    # mark DA-T2V and arXiv-T2V with red color
    for label in plt.gca().get_xticklabels():
        if label.get_text() in ["DA-T2V", "arXiv-T2V"]:
            label.set_color('red')
        else:
            label.set_color('black')
    
    plt.tight_layout()
    plt.savefig("data/p2-analysis2/analysis2-plottypes-comparison.pdf", dpi=300)
    plt.show()
    
    
    