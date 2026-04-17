import glob
import os
import json
import nbformat
from tqdm import tqdm


if __name__ == "__main__":
    glob_path = "/Users/nngu0448/Documents/data/Text2Chart31-Dataset/Text2Chart31-test/*/t2v_notebook_true/*_log"
    log_dirs = sorted(glob.glob(glob_path))
    print(f"Found {len(log_dirs)} log directories for dataset Text2Chart31")
    
    for log_dir in tqdm(log_dirs):
        log_data_paths = sorted(glob.glob(os.path.join(log_dir, "*.json")))
        
        subplot_ids = set()
        
        for log_data_path in log_data_paths:
            if "variables.json" in log_data_path:
                continue

            subplot_id = os.path.basename(log_data_path).rsplit("_", maxsplit=1)[0]
            subplot_ids.add(subplot_id)

        print(log_dir, len(subplot_ids), subplot_ids)
        