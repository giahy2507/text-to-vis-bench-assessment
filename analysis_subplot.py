import glob
import json
import os
import nbformat
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd
import altair


def main_analysis_subplot_python_based():
    dataset = "arXiv-T2V"
    
    glob_path = None
    glob_path_2 = None
    if dataset == "ChartX":
        glob_path = "/Users/nngu0448/Documents/data/ChartX-Dataset/my_parsing/*/*-multi-axes*/t2v_notebook_true/*_log"
    elif dataset == "Text2Chart31":
        glob_path = "/Users/nngu0448/Documents/data/Text2Chart31-Dataset/Text2Chart31-test/*/t2v_notebook_true/*_log"
    elif dataset == "GitHub-T2V":
        glob_path = "/Users/nngu0448/Documents/data/T2V-Phase2-Experiments/github-v2/github-v2_human-nlr_codex-gpt5_1/*/t2v_gt/*_log"
    elif dataset == "arXiv-T2V":
        glob_path = "/Users/nngu0448/Documents/data/T2V-Phase2-Experiments/arxiv-v3/arxiv-v3_human-nlr_codex-gpt5_1/*/t2v_gt/*_log"
        glob_path_2 = "/Users/nngu0448/Documents/data/T2V-Phase2-Experiments/arxiv-v32/gpt-5/human-nlr/arxiv-v32-pred-1/*/t2v_gt/*_log"
    elif dataset == "OWID-T2V":
        glob_path = "/Users/nngu0448/Documents/data/T2V-Phase2-Experiments/owid-v6/owid-v6_machine-nlr_codex-gpt5_1/*/t2v_gt/*_log"
    else:
        raise ValueError("Unknown dataset")
    log_dirs = sorted(glob.glob(glob_path))
    if glob_path_2:
        log_dirs += sorted(glob.glob(glob_path_2))
    print(f"Found {len(log_dirs)} log directories for dataset {dataset}")
    # Prepare data for analysis
    
    save_data = []
    
    for log_dir in tqdm(log_dirs):
        log_data_paths = sorted(glob.glob(os.path.join(log_dir, "*.json")))
        
        subplot_ids = set()
        for log_data_path in log_data_paths:
            if "variables.json" in log_data_path:
                continue

            subplot_id = os.path.basename(log_data_path).rsplit("_", maxsplit=1)[0]
            subplot_ids.add(subplot_id)

        print(log_dir, len(subplot_ids), subplot_ids)
        save_data.append({
            "log_dir": log_dir,
            "distinct_subplot_count": len(subplot_ids),
            "subplot_ids": list(subplot_ids)
        })

    # add row for average subplot count
    total_subplot_count = sum(item["distinct_subplot_count"] for item in save_data)
    average_subplot_count = total_subplot_count / len(save_data)
    save_data.append({
        "log_dir": "Average",
        "distinct_subplot_count": average_subplot_count,
        "subplot_ids": []
    })
    
    # save the data to csv
    df = pd.DataFrame(save_data)
    output_path = f"data/p2-analysis1/subplot-count/{dataset}_subplot-analysis.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

def nlv_corpus():
    dataset = "NLV-Corpus"
    
    num_subplot_dict = {
        "superstore-groupedBar": 4,
        "superstore-scatterFaceted": 4,
        "movies-groupedBar": 4,
        "movies-scatterFaceted": 4,
        "cars-groupedBar": 5,
        "cars-scatterFaceted": 3
    }


    vlspecs_path = "/Users/nngu0448/Documents/data/NLV-Corpus/vlSpecs.json"
    nlv_corpus_path = '/Users/nngu0448/Documents/data/NLV-Corpus/NLV Corpus.csv'
    
    nlv_corpus = pd.read_csv(nlv_corpus_path, encoding="utf-8")
    print(nlv_corpus.head())
    
    data = []
    
    for i, row in nlv_corpus.iterrows():
        utterance = row["Utterance Set"]
        vis_id = row["visId"]
        ds = row["dataset"].lower()

        dataset_vis_id = f"{ds}-{vis_id}"
        num_subplot = num_subplot_dict.get(dataset_vis_id, 1)

        data.append({
           "utterance": utterance,
           "vis_id": vis_id,
           "dataset": ds,
           "num_subplot": num_subplot
       })

    # Convert to DataFrame
    df = pd.DataFrame(data)
    print(df.head())
    
    # add averages
    avg_row = {
        "utterance": "Average",
        "vis_id": "",
        "dataset": "",
        "num_subplot": df["num_subplot"].mean()
    }
    df = df._append(avg_row, ignore_index=True)

    # Save the DataFrame to a CSV file
    output_path = f"data/p2-analysis1/subplot-count/{dataset}_subplot-count.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    

if __name__ == "__main__":
    main_analysis_subplot_python_based()
    
    
    
    
