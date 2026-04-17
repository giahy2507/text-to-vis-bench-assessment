import json
import os

if __name__ == "__main__":
    json_path = "/Users/nngu0448/Documents/data/nvBench2.0-dataset/test.json"
    
    output_dir = "/Users/nngu0448/Documents/data/nvBench2.0-dataset/t2v-dataset"
    
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
        for idx, item in enumerate(data):
            csv_file = item["csv_file"]
            nl_query = item["nl_query"]
            table_schema = item["table_schema"]
            steps = item["steps"]
            gold_answer = item["gold_answer"]
            
            sample_id = "test_" + str(idx).zfill(5)
            sample_dir = os.path.join(output_dir, sample_id)
            os.makedirs(sample_dir, exist_ok=True)
            
            gt_t2v_dir = os.path.join(sample_dir, "t2v_gt")
            os.makedirs(gt_t2v_dir, exist_ok=True)
            
            # save python code to file
            source = \
f"""
{csv_file}

{table_schema}

{nl_query}

{steps}

##START VISUALISATION CODE

{gold_answer}

##END VISUALISATION CODE
"""
            code_file_path = os.path.join(gt_t2v_dir, f"{sample_id}.py")
            with open(code_file_path, "w", encoding="utf-8") as code_f:
                code_f.write(source)
            