from collections import OrderedDict, defaultdict
import json
import glob
import os
from tqdm import tqdm


def main_convert_R_usage_to_universal_usage():
    
    input_dir = "data/raw-data/the-stack/R_Graphics/"
    glob_path = os.path.join(input_dir, "*.r.txt")

    output_file_path = "data/universal/Graphics_R.universal2.jsonl"
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    fo = open(output_file_path, mode="w", encoding="utf-8")

    paths = sorted(glob.glob(glob_path))
    for file_path in tqdm(paths):
        items = []
        print(file_path)
        with open(file_path, mode="r", encoding="utf-8") as file:
            item = ""
            for line in file:
                if line.strip() == "--------------------":
                    if item:
                        items.append(item.strip())
                    item = ""
                else:
                    item += line
            if item:
                items.append(item.strip())
        if len(items) == 0:
            continue
        
        file_id = os.path.basename(file_path).replace(".r.txt", "")
        universal_items = []

        for item in items:
            seqs = item.split("\n")
            assert len(seqs) == 3
            func_name = seqs[0]
            args = json.loads(seqs[1])
            kargs = json.loads(seqs[2])
            if len(kargs) == 0 or isinstance(kargs, list):
                kargs = dict()
                
            # processing args
            new_args = []
            for arg_value in args:
                arg_value = arg_value[0] if len(arg_value) ==1 else "".join(arg_value)
                new_args.append(arg_value)
            
            # processing kargs
            new_kargs = OrderedDict()
            for key, value in kargs.items():
                value = value[0] if len(value) ==1 else "".join(value)
                new_kargs[key] = [value.strip("\"")]

            universal_items.append({
                "var_call": "None",
                "func_name": func_name,
                "args": new_args,
                "kargs": new_kargs,
                "target_lib": "graphics"
            })

        if len(universal_items) > 0:
            fo.write(json.dumps({
                "file_id": file_id,
                "content": universal_items
            }, ensure_ascii=False) + "\n")

    fo.close()
        
    
if __name__ == "__main__":
    main_convert_R_usage_to_universal_usage()





    

    
