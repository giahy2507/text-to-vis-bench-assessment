import glob
import os
import json
import pandas as pd
from tqdm import tqdm

if __name__ == "__main__":
    dataset = "GitHub"
    
    if dataset == "REDCap":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/Version_1/round_*/*/annotations/t2v_json_true/*.json"
        t2v_sample_paths = glob.glob(glob_path)
    elif dataset == "GitHub":
        glob_path = "/Users/nngu0448/Documents/data/github-data/Version_1/*/*/t2v_json_true/*.json"
        t2v_sample_paths = glob.glob(glob_path)
    else:
        raise ValueError("Unknown dataset")

    t2v_sample_paths = sorted(t2v_sample_paths)
    print(f"Found {len(t2v_sample_paths)} notebooks in {dataset} dataset.")
    
    stats = {}
    
    for t2v_sample_path in tqdm(t2v_sample_paths):
        assert os.path.exists(t2v_sample_path), f"Path {t2v_sample_path} does not exist."
        
        with open(t2v_sample_path, "r", encoding="utf-8") as f:
            t2v_data = json.load(f)
        
        len_input = 0
        len_output = 0
        for cell in t2v_data:
            if "t2v_cell_type" not in cell:
                print(f"Missing 't2v_cell_type' in {t2v_sample_path}")
                raise KeyError(f"Missing 't2v_cell_type' in {t2v_sample_path}")
            
            if cell["t2v_cell_type"].startswith("input"):
                len_input += len(cell["source"])
            elif cell["t2v_cell_type"].startswith("output"):
                len_output += len(cell["source"])
            else:
                print(f"Unknown cell type: {cell['t2v_cell_type']} in {t2v_sample_path}")
                raise ValueError(f"Unknown cell type: {cell['t2v_cell_type']}")

        stats[t2v_sample_path] = {
            "input_length": len_input,
            "output_length": len_output,
            "total_length": len_input + len_output
        }
    
    # calculate average input, output, and total length
    avg_input_length = sum(stat["input_length"] for stat in stats.values()) / len(stats)
    avg_output_length = sum(stat["output_length"] for stat in stats.values()) / len(stats)
    avg_total_length = sum(stat["total_length"] for stat in stats.values()) / len(stats)
    
    # add averages to stats
    stats["averages"] = {
        "input_length": avg_input_length,
        "output_length": avg_output_length,
        "total_length": avg_total_length
    }
    
    
    # Write stats to a csv file
    output_path = f"data/analysis-result-p2/t2v_sample_length/{dataset}_t2v_sample_length.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame.from_dict(stats, orient="index")
    df.to_csv(output_path, index_label="t2v_sample_path")
        
