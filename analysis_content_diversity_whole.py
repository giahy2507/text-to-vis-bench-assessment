from transformers import GPT2Tokenizer, BertTokenizer
from typing import List
import glob
import os
import nbformat
import tqdm
import pandas as pd
import json

# initialize GPT2 tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# initialize BERT tokenizer
# tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")


def text_to_kgram(text) -> List[str]:
    """
    Convert text to k-grams.
    
    Args:
        text (str): Input text string.
        
    Returns:
        List[str]: List of k-grams.
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)

    return [tuple(tokens[i:i + 1]) for i in range(len(tokens) - 1)]


def compute_distinct_k(t2v_sample_paths, k: int, source_type: str) -> float:
    """
    Compute distinct-k for a list of T2V sample paths.
    """
    assert k >= 1, "k must be >= 1"

    distinct_k_grams = set()
    total_k_grams = 0
    
    for t2v_sample_path in tqdm.tqdm(t2v_sample_paths):
        if not os.path.exists(t2v_sample_path):
            continue
        
        with open(t2v_sample_path, "r", encoding="utf-8") as f:
            t2v_data = json.load(f)
        
        input_source = ""
        output_source = ""
        
        for cell in t2v_data:
            if "t2v_cell_type" not in cell:
                print(f"Missing 't2v_cell_type' in {t2v_sample_path}")
                raise KeyError(f"Missing 't2v_cell_type' in {t2v_sample_path}")
            
            if cell["t2v_cell_type"].startswith("input"):
                input_source += cell["source"] + "\n"
            elif cell["t2v_cell_type"].startswith("output"):
                output_source += cell["source"] + "\n"
            else:
                print(f"Unknown cell type: {cell['t2v_cell_type']} in {t2v_sample_path}")
                raise ValueError(f"Unknown cell type: {cell['t2v_cell_type']}")

        text_content = input_source if source_type == "input" else output_source
        
        tokens = tokenizer.encode(text_content, add_special_tokens=False)
        total_tokens = len(tokens)

        if total_tokens < k:
            continue

        k_grams = [tuple(tokens[i:i+k]) for i in range(total_tokens - k + 1)]
        distinct_k_grams.update(k_grams)
        total_k_grams += len(k_grams)

    if total_k_grams == 0:
        return 0.0

    return len(distinct_k_grams) / total_k_grams

def compute_distinct_k_new(file_paths, k: int, source_type: str) -> float:
    """
    Compute distinct-k for a list of T2V sample paths.
    """
    assert k >= 1, "k must be >= 1"

    distinct_k_grams = set()
    total_k_grams = 0
    
    for file_path in tqdm.tqdm(file_paths):
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

        text_content = input_content if source_type == "input" else output_content
        
        tokens = tokenizer.encode(text_content, add_special_tokens=False)
        total_tokens = len(tokens)

        if total_tokens < k:
            continue

        k_grams = [tuple(tokens[i:i+k]) for i in range(total_tokens - k + 1)]
        distinct_k_grams.update(k_grams)
        total_k_grams += len(k_grams)

    if total_k_grams == 0:
        return 0.0

    return len(distinct_k_grams) / total_k_grams

def compute_distinct_k_jsonl(jsonl_path: str, k: int, source_type: str) -> float:
    """
    Compute distinct-k for a JSONL file.
    """
    assert k >= 1, "k must be >= 1"

    distinct_k_grams = set()
    total_k_grams = 0

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in tqdm.tqdm(f):
            json_data = json.loads(line.strip())

            input_source = json_data["input_source"]
            output_source = json_data["output_source"]

            text_content = input_source if source_type == "input" else output_source

            tokens = tokenizer.encode(text_content, add_special_tokens=False)
            total_tokens = len(tokens)

            if total_tokens < k:
                continue

            k_grams = [tuple(tokens[i:i+k]) for i in range(total_tokens - k + 1)]
            distinct_k_grams.update(k_grams)
            total_k_grams += len(k_grams)

    if total_k_grams == 0:
        return 0.0

    return len(distinct_k_grams) / total_k_grams


if __name__ == "__main__":
    k_min = 3
    k_max = 3
    
    data = []
    # datasets = ["GitHub-T2V", "arXiv-T2V", "OWID-T2V", "Text2Chart31", "ChartX", "NLV-Corpus", "nvBench"]
    # datasets = ["GitHub-T2V", "arXiv-T2V", "OWID-T2V"]
    datasets = ["OWID-T2V"]

    for dataset in datasets:
        if dataset == "GitHub-T2V":
            glob_path = "/Users/nngu0448/Documents/data/github-data/github-v2/test*/t2v_gt/test*.py"
            t2v_sample_paths = sorted(glob.glob(glob_path))
        elif dataset == "arXiv-T2V":
            glob_path = "/Users/nngu0448/Documents/data/REDCap-VisReflect/arxiv-v3/r*/t2v_gt/r*.py"
            t2v_sample_paths = sorted(glob.glob(glob_path))
            glob_path_2 = "/Users/nngu0448/Documents/data/REDCap-VisReflect/arxiv-v32/r*/t2v_gt/r*.py"
            t2v_sample_paths += sorted(glob.glob(glob_path_2))
        elif dataset == "OWID-T2V":
            glob_path = "/Users/nngu0448/Documents/data/T2V-Phase2-Experiments/owid-v6/gpt-5/owid-v6-pred-1/*/t2v_pred/*.vis-request.txt"
            t2v_sample_paths = sorted(glob.glob(glob_path))
        elif dataset == "nvBench2.0":
            glob_path = "/Users/nngu0448/Documents/data/nvBench2.0-dataset/t2v-dataset/*/t2v_gt/test*.py"
            t2v_sample_paths = sorted(glob.glob(glob_path))
            
        elif dataset == "ChartX":
            glob_path = "/Users/nngu0448/Documents/data/ChartX-Dataset/my_parsing/*/*/t2v_json_true/*.json"
            t2v_sample_paths = glob.glob(glob_path)
        elif dataset == "Text2Chart31":
            glob_path = "/Users/nngu0448/Documents/data/Text2Chart31-Dataset/Text2Chart31-test/*/t2v_json_true/*.json"
            t2v_sample_paths = glob.glob(glob_path)
        elif dataset == "NLV-Corpus":
            t2v_sample_paths = ["/Users/nngu0448/Documents/data/NLV-Corpus/NLV_Corpus.jsonl"]
        elif dataset == "nvBench":
            t2v_sample_paths = ["/Users/nngu0448/Documents/data/nvBench-dataset/nvBench_val_test.jsonl"]
        else:
            raise ValueError("Unknown dataset")

        
        t2v_sample_paths = sorted(t2v_sample_paths)
        print(f"Processing {len(t2v_sample_paths)} notebooks for dataset {dataset}")
        
        for source_type in ["input", "output"]:
        
            for k in range(k_min, k_max + 1):
                if dataset in ["GitHub-T2V", "arXiv-T2V", "OWID-T2V", "nvBench2.0"]:
                    distinct_k_value = compute_distinct_k_new(t2v_sample_paths, k, source_type)
                elif dataset in ["NLV-Corpus", "nvBench"]:
                    distinct_k_value = compute_distinct_k_jsonl(t2v_sample_paths[0], k, source_type)
                else:
                    distinct_k_value = compute_distinct_k(t2v_sample_paths, k, source_type)
                data.append({
                    "dataset": dataset,
                    "source_type": source_type,
                    "k": k,
                    "distinct_k": distinct_k_value
                })
                print(f"Source type {source_type} Distinct-{k}: {distinct_k_value}")
            
    # Save the results to a CSV file
    df = pd.DataFrame(data)
    
    # sort by dataset and k
    df = df.sort_values(by=["dataset", "source_type", "k"])

    output_path = f"data/p2-analysis1/content-diversity-wholedataset/content_diversity-OUR-datasets-k=3.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")
    print("Analysis complete.")
