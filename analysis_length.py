import glob
import os
import json
import pandas as pd
from tqdm import tqdm
from utils import tokenize_text


def main_calculate_for_python_based(dataset):
    
    if dataset == "arXiv-T2V":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/Version_1/round_*/*/annotations/t2v_json_true/*.json"
        t2v_sample_paths = glob.glob(glob_path)
    elif dataset == "DA-T2V":
        glob_path = "/Users/nngu0448/Documents/data/github-data/Version_1/*/*/t2v_json_true/*.json"
        t2v_sample_paths = glob.glob(glob_path)
    elif dataset == "ChartX":
        glob_path = "/Users/nngu0448/Documents/data/ChartX-Dataset/my_parsing/*/*/t2v_json_true/*.json"
        t2v_sample_paths = glob.glob(glob_path)
    elif dataset == "Text2Chart31":
        glob_path = "/Users/nngu0448/Documents/data/Text2Chart31-Dataset/Text2Chart31-test/*/t2v_json_true/*.json"
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
    output_path = f"data/p2-analysis1/io_length/{dataset}_t2v_sample_length.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame.from_dict(stats, orient="index")
    df.to_csv(output_path, index_label="t2v_sample_path")


def main_calculate_for_vegalite_based():
    
    dataset = "NLV-Corpus"
    if dataset == "nvBench":
        jsonl_data_path = "/Users/nngu0448/Documents/data/nvBench-dataset/nvBench_val_test.jsonl"
    elif dataset == "NLV-Corpus":
        jsonl_data_path = "/Users/nngu0448/Documents/data/NLV-Corpus/NLV_Corpus.jsonl"
        
    
    with open(jsonl_data_path, "r", encoding="utf-8") as f:
        data_samples = []
        for line in tqdm(f, desc=f"Processing {dataset} data samples"):
            sample = json.loads(line)
            input_length = len(sample["input_source"])
            output_length = len(sample["output_source"])
            total_length = input_length + output_length
            _id = sample["_id"].replace("\n", "").strip()
            
            data_samples.append({
                "_id": _id,
                "input_length": input_length,
                "output_length": output_length,
                "total_length": total_length
            })
    
    df = pd.DataFrame(data_samples)
    avg_row = {
        "_id": "Average",
        "input_length": df["input_length"].mean(),
        "output_length": df["output_length"].mean(),
        "total_length": df["total_length"].mean()
    }
    df = df._append(avg_row, ignore_index=True)
    
    output_path = f"data/p2-analysis1/io_length/{dataset}_length.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {dataset} data sample lengths to {output_path}")

def main_calculate_for_python_new_format():
    dataset = "OWID-T2V"
    
    glob_path = None
    glob_path_2 = None
    if dataset == "GitHub-T2V":
        glob_path = "/Users/nngu0448/Documents/data/github-data/github-v2/test*/t2v_gt/test*.py"
    elif dataset == "arXiv-T2V":
        glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/arxiv-v3/r*/t2v_gt/r*.py"
        glob_path_2 = "/Users/nngu0448/Documents/data/REDCap-VisReflect/arxiv-v32/r*/t2v_gt/r*.py"
    elif dataset == "OWID-T2V":
        glob_path = "/Users/nngu0448/Documents/data/T2V-Phase2-Experiments/owid-v6/gpt-5/owid-v6-pred-1/*/t2v_pred/*.vis-request.txt"
    elif dataset == "nvBench2.0":
        glob_path = "/Users/nngu0448/Documents/data/nvBench2.0-dataset/t2v-dataset/*/t2v_gt/test*.py"
    else:
        raise ValueError("Unknown dataset")
    
    file_paths = sorted(glob.glob(glob_path))
    if glob_path_2 is not None:
        file_paths += sorted(glob.glob(glob_path_2))
    print(f"Found {len(file_paths)} files in {dataset} dataset.")
    stats = {}
    
    for file_path in tqdm(file_paths):
        if file_path.endswith(".py"):
            code_content = open(file_path, "r", encoding="utf-8").read()
            
            # replace "##END VISUALISATION CODE" by ""
            code_content = code_content.replace("##END VISUALISATION CODE", "")
            
            # split by "##START VISUALISATION CODE"
            seqs = code_content.split("##START VISUALISATION CODE")
            assert len(seqs) == 2, f"Unexpected format in {file_path}"
            input_content, output_content = seqs
        elif file_path.endswith(".vis-request.txt"):
            vis_request_content = open(file_path, "r", encoding="utf-8").read()
            input_content = vis_request_content
            output_content = ""
        
        stats[file_path] = {
            "input_length": len(input_content),
            "output_length": len(output_content),
            "total_length": len(input_content) + len(output_content)
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
    output_path = f"data/p2-analysis1/io_length/{dataset}_io_length.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame.from_dict(stats, orient="index")
    df.to_csv(output_path, index_label="file_path")
    

if __name__ == "__main__":
    # main_calculate_for_python_based(dataset="DA-T2V")
    # main_calculate_for_python_based(dataset="arXiv-T2V")
    # main_calculate_for_vegalite_based()
    
    main_calculate_for_python_new_format()

    
    
    
