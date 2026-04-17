import altair as alt
import json
import pandas as pd
import os
import random
import hashlib

def main_convert_nlv_corpus():
    vlspecs_dir = "/Users/nngu0448/Documents/data/NLV-Corpus/vlSpecs"
    vlspecs_path = "/Users/nngu0448/Documents/data/NLV-Corpus/vlSpecs.json"
    vlspecs = json.load(open(vlspecs_path, "r", encoding="utf-8"))
    print(f"Found {len(vlspecs)} VLSpecs in {vlspecs_path}")

    nlv_corpus_path = '/Users/nngu0448/Documents/data/NLV-Corpus/NLV Corpus.csv'
    nlv_corpus = pd.read_csv(nlv_corpus_path, encoding="utf-8")
    print(nlv_corpus.head())

    jsonl_data = []

    for i, row in nlv_corpus.iterrows():
        utterance = row["Utterance Set"]
        vis_id = row["visId"]
        dataset = row["dataset"].lower()
        
        vis_spec = vlspecs.get(f"{dataset}-{vis_id}", {})

        if "superstore" in vis_id:
            continue
        
        hexsha = hashlib.sha1(f"{dataset}-{vis_id}-{utterance}".encode("utf-8")).hexdigest()
        jsonl_data.append({
            "_id": f"{dataset}-{vis_id}-{utterance}",
            "plot_type": vis_id,
            "utterance": utterance,
            "hexsha": hexsha,
            "content": json.dumps(vis_spec, ensure_ascii=False),
            "input_source": utterance,
            "output_source": json.dumps(vis_spec, ensure_ascii=False),
        })

    # Save the jsonl data to a file
    jsonl_file_path = "/Users/nngu0448/Documents/data/NLV-Corpus/NLV_Corpus.jsonl"
    with open(jsonl_file_path, "w", encoding="utf-8") as f:
        for entry in jsonl_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            

if __name__ == "__main__":
    main_convert_nlv_corpus()
    
            
    
        