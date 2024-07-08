import json
from collections import defaultdict
from tqdm import tqdm


def main_count_unique_func_args(universal_dir, dataset_name):
    univeral_data_path = f"{universal_dir}/{dataset_name}.universal2.jsonl"
    
    with open(univeral_data_path, mode="r", encoding="utf-8") as fi:
        y_unique_func = []
        y_unique_func_args = []
        for line in tqdm(fi, leave=False):
            json_objs = json.loads(line)["content"]
            file_func_dict = defaultdict(int)
            file_func_args_dict = defaultdict(int)

            for json_obj in json_objs:
                func_name = json_obj["func_name"]
                # filter data functions (data processing)
                if dataset_name == "Vegalite_Vega" or dataset_name == "nvBench_Vegalite_Vega":
                    if func_name.startswith("data|"):
                        continue
                
                # counting
                file_func_dict[func_name] += 1
                for karg, karg_value in json_obj["kargs"].items():
                    file_func_args_dict[f"{func_name}|{karg}"] += len(karg_value)
                for i, arg in enumerate(json_obj["args"]):
                    file_func_args_dict[f"{func_name}|args_{i}"] += 1

            if len(file_func_dict) == 0:
                continue
            y_unique_func.append(len(file_func_dict))
            y_unique_func_args.append(len(file_func_args_dict))

    print(dataset_name)
    average = sum(y_unique_func)/len(y_unique_func)
    print("Average No. Unique Func: ", average)
    average_2 = sum(y_unique_func_args)/len(y_unique_func_args)
    print("Average No. Unique Func| Args: ", average_2)
    print("------"*10)


if __name__ == "__main__":
    universal_dir = "data/universal"
    for dataset_name in ["Matplotlib_Python",
                         "Matplotlib_Notebook", 
                         "Graphics_R", 
                         "ChartJS_JavaScript", 
                         "Vegalite_Vega", 
                         "ChartDialog_Matplotlib_Python", 
                         "PlotCoder_Matplotlib_Python", 
                         "nvBench_Vegalite_Vega"]:
        
        main_count_unique_func_args(universal_dir=universal_dir, 
                                    dataset_name=dataset_name)
    
    
    



    
    

