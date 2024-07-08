import json
from tqdm import tqdm
import os
from collections import defaultdict
import subprocess


def get_file_length(path):
    assert os.path.isfile(path)
    s = subprocess.check_output(f"wc -l {path}", shell = True)
    s = s.decode("utf-8").strip()
    length = s.split()[0]
    return int(length)

def write_to_tsv_file(stats_result, 
                      output_path, 
                      dataset_name,
                      is_args=False, 
                      output_percentage=False):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, mode="w", encoding="utf-8") as fo:
        if not is_args:
            fo.write(f"func_name\tfreq\n")
        else:
            fo.write(f"func_name|arg\tfreq\n")
        
        sum_freq = sum([1 for _, freq in stats_result])
        for i , func_name_count in enumerate(stats_result):
            func_name, count = func_name_count
            if dataset_name in ["Vegalite_Vega", "nvBench_Vegalite_Vega"] and func_name.startswith("data"):
                continue
            if not output_percentage:
                fo.write(f"{func_name}\t{count}\n")
            else:
                fo.write(f"{func_name}\t{count}\t{(i/sum_freq)*100:.2f}\n")

def get_top_k_func(universal_paths, 
                   topk=50, 
                   target_func_names=None, 
                   dataset_name=None):
    result = defaultdict(int)
    for path in tqdm(universal_paths, leave=False):
        with open(path, mode="r", encoding="utf-8") as fi:
            for line in tqdm(fi, leave=False):
                line = line.strip()
                if line != "":
                    json_objs = json.loads(line)["content"]
                    
                    for json_obj in json_objs:
                        func_name = json_obj["func_name"]
                        
                        # filter by target_func_names
                        if target_func_names is not None:
                            if func_name not in target_func_names:
                                continue

                        if dataset_name in ["ChartJS_JavaScript", "Vegalite_Vega", "nvBench_Vegalite_Vega"]:
                            # In universal format of JSON-based language: one function can be called multiple times --> multiple values for a specific karg. 
                            # This is because we post-process the JSON to a flat-version, as exemplified below.
                            # We count the maximum number of value over kargs
                            no_values = []
                            for karg_key, karg_value in json_obj["kargs"].items():
                                no_values.append(len(karg_value))
                            max_no_values = max(no_values)
                            result[func_name] += max_no_values
                        else:
                            result[func_name] += 1
    result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    if topk == -1 or topk is None:
        return result
    else:
        return result[:min(topk, len(result))]

"""
https://vega.github.io/vega-lite/examples/vconcat_weather.html
For example, in the universal format, we have the following JSON:
{
    ...
    "vconcat": [
        {
            "mark": "bar",
            ...
        },
        {
            "mark": "point",
            ...
        }
    ]
}
We post-process the JSON to a flat-version, as exemplified below:
"vconcat|mark": ["bar", "point"],
--> Which means that the function "vconcat" is called 2 times with the karg "mark" having values "bar" and "point"
If we have multiple kargs, we need to get the maximum number of values over kargs --> to could the frequency of the function
"""

def get_top_kargs(universal_paths, topk=None):
    all_args_value_dict = defaultdict(list)
    for path in tqdm(universal_paths, leave=False):
        with open(path, mode="r", encoding="utf-8") as fi:
            for line in tqdm(fi, leave=False):
                line = line.strip()
                if line != "":
                    json_objs = json.loads(line)["content"]
                    for json_obj in json_objs:
                        func_name = json_obj["func_name"]
                        for karg_key, karg_value in json_obj["kargs"].items():
                            for value in karg_value:
                                all_args_value_dict[f"{func_name}|{karg_key}"].append(str(value))

    # sort all_args_value_dict
    all_args_value_dict = sorted(all_args_value_dict.items(), key=lambda x: len(x[1]), reverse=True)
    all_args_freq = [(key, len(value)) for key, value in all_args_value_dict]
    if topk is not None:
        all_args_freq = all_args_freq[:min(topk, len(all_args_freq))]

    return all_args_freq

def main_count_funcname_args(dataset_name, 
                             universal_dir, 
                             counting_dir):
    top_k_func = None
    top_k_args = None

    univeral_data_path = f"{universal_dir}/{dataset_name}.universal2.jsonl"
    universal_paths = [univeral_data_path]
    
    no_lines = sum([get_file_length(path) for path in universal_paths])
    print(dataset_name, f"# files: {len(universal_paths)}", f"# records: {no_lines}", sep="\t")
    
    # Observation 1: top k functions --> top k args
    stats_func = get_top_k_func(universal_paths=universal_paths, 
                                topk=top_k_func, 
                                dataset_name=dataset_name)
    write_to_tsv_file(stats_func, dataset_name=dataset_name,
                      output_path=f"{counting_dir}/{dataset_name}/top_all_func.tsv")
    
    ## Observation 2: top k args 
    stats_func_args = get_top_kargs(universal_paths=universal_paths, 
                                    topk=top_k_args)
    write_to_tsv_file(stats_func_args, dataset_name=dataset_name,
                      output_path=f"{counting_dir}/{dataset_name}/top_all_func_args.tsv",
                      is_args=True, 
                      output_percentage=True)
    print("--"*50)


def check_func_arg_in_universal_file(func_name, arg_name, universal_path):
    with open(universal_path, mode="r", encoding="utf-8") as fi:
        for line in fi:
            line = line.strip()
            if line != "":
                json_obj = json.loads(line)
                if json_obj["func_name"] == func_name:
                    if arg_name in json_obj["kargs"]:
                        return True
    return False


if __name__ == "__main__":
    
    counting_dir = "data/counting"
    universal_dir = "data/universal"

    for dataset_name in ["Matplotlib_Python",
                         "Matplotlib_Notebook", 
                         "Graphics_R", 
                         "ChartJS_JavaScript", 
                         "Vegalite_Vega", 
                         "ChartDialog_Matplotlib_Python", 
                         "PlotCoder_Matplotlib_Python", 
                         "nvBench_Vegalite_Vega"]:
        
        main_count_funcname_args(dataset_name=dataset_name, 
                                 universal_dir=universal_dir,
                                 counting_dir=counting_dir)


    

    
