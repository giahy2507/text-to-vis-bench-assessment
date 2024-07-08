from datasets import load_dataset
from pprint import pprint
import json
from tqdm import tqdm
import os
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_name', type=str)
    parser.add_argument('--lang_dir', type=str)
    parser.add_argument('--output_dir', type=str)  
    parser.add_argument('--hugging_face_token', type=str)
    args = parser.parse_known_args()[0]

    output_dir = args.output_dir
    dataset_name = args.dataset_name
    lang_dir = args.lang_dir
    hugging_face_token = args.hugging_face_token

    os.makedirs(output_dir, exist_ok=True)   
    ds = load_dataset(dataset_name, 
                    # streaming=True,
                    data_dir=lang_dir,
                    split="train",
                    use_auth_token=hugging_face_token)
    
    for item in tqdm(ds):
        lang = item["lang"]
        # writing the item as jsonl
        with open(f"{output_dir}/{lang}.jsonl", mode="a", encoding="utf-8") as fo:
            fo.write(json.dumps(item, ensure_ascii=False)+"\n")
        