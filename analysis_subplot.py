import glob
import json
import os
import nbformat
from collections import defaultdict
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd


if __name__ == "__main__":
    dataset = "Github"
    
    if dataset == "Github":
        glob_path = "/Users/nngu0448/Documents/data/github-data/Version_1/*/*/t2v_notebook_true/*_log"
    elif dataset == "REDCap":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/Version_1/round_*/*/annotations/t2v_notebook_true/*_log"
    else:
        raise ValueError("Unknown dataset")
    log_dirs = sorted(glob.glob(glob_path))
    
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
    output_path = f"data/analysis-result-p2/subplot-count/{dataset}_subplot-analysis.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
