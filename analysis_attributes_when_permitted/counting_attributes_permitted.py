from utils import load_tsv_file
import json
import os
from tqdm import tqdm
from collections import defaultdict, OrderedDict

def extract_special_counting_for_dataset(universal_dir, 
                                         dataset_name):
    # Counting of special cases, such as "plt.axis('off')", "spines['top'].set_visible", ...
    special_cases_path = f"{universal_dir}/special_cases.tsv"
    special_cases = load_tsv_file(special_cases_path, 
                                  return_dict=False)

    result = {}
    for item in special_cases:
        if item[0] == dataset_name:
            result[item[1]] = item[2]
    return result

def main_count_attributes_when_permitted(counting_dir,
                                            universal_dir, 
                                            mapping_dir,
                                            dataset_name, verbose=False):
    # Load mappings for a dataset
    attributes_path = f"{mapping_dir}/attributes/{dataset_name}.json"
    attributes_list = json.load(open(attributes_path, mode="r", encoding="utf-8"))

    # Load frequency of functions and arguments
    tsv_stats_func_path = f"{counting_dir}/{dataset_name}/top_all_func.tsv"
    dataset_stats_func = load_tsv_file(tsv_stats_func_path, return_dict=True)
    tsv_stats_args_path = f"{counting_dir}/{dataset_name}/top_all_func_args.tsv"
    dataset_stats_args = load_tsv_file(tsv_stats_args_path, return_dict=True)
    
    # load special counting cases for the dataset
    dataset_special_cases = extract_special_counting_for_dataset(universal_dir=universal_dir, 
                                                                 dataset_name=dataset_name)

    # load programs
    universal_path = f"{universal_dir}/{dataset_name}.universal2.jsonl"
    assert os.path.isfile(universal_path)
    universal_lines = open(universal_path, mode="r", encoding="utf-8").readlines()

    if verbose:
        print(f"Dataset: {dataset_name}")

    # counting
    result = OrderedDict()
    for default_attributes_dict in attributes_list:
        category = default_attributes_dict["category"]
        attribute = default_attributes_dict["attribute"]
        affecting_level = default_attributes_dict["affecting_level"]
        params_with_default_values = default_attributes_dict["params_with_default_values"]

        assert affecting_level in ["Command", "Program"], f"Unknown affecting level: {affecting_level}"
        if affecting_level == "Command":
            # Command level 
            unique_func_counter = {}
            unuque_args_counter = {}
            for karg_key, _ in params_with_default_values.items():
                if karg_key in dataset_stats_args:
                    func_name, _ = karg_key.rsplit("|", maxsplit=1)
                    unique_func_counter[func_name] = dataset_stats_func[func_name]
                    unuque_args_counter[karg_key] = dataset_stats_args[karg_key]
            
                # # Special_cases
                if karg_key in dataset_special_cases:
                    unuque_args_counter[karg_key] = dataset_special_cases[karg_key]
                
            sum_args_counter = sum([int(v) for v in unuque_args_counter.values()]) # --> k
            sum_func_counter = max(sum([int(v) for v in unique_func_counter.values()]), 1) # --> p
            ratio = (sum_args_counter/sum_func_counter)*100
        else:
            # Program level
            counter = 0 # --> g
            for line in tqdm(universal_lines, leave=False):
                program_json_data = json.loads(line.strip())
                program_content = program_json_data["content"]
                if len(program_content) == 0:
                    continue
                is_used = check_program_usage(program_content, params_with_default_values)
                if is_used is True:
                    counter +=1

            # Handle special cases which were counted on the program level
            for karg_key, _ in params_with_default_values.items():
                if karg_key in dataset_special_cases:
                    counter += int(dataset_special_cases[karg_key])
            
            total = len(universal_lines) # --> z
            ratio = (counter/total)*100

        # Normalize
        if ratio > 100: 
            ratio = 100 
        
        if (category, attribute) not in result:
            result[(category, attribute)] = OrderedDict()

        result[(category, attribute)][dataset_name] = f"{ratio:.1f}"
        if verbose:
            print(category, attribute, affecting_level, f"{ratio:.1f}")
    
    if verbose:
        print("------"*10)

    return result


def check_program_usage(program_content, 
                        considered_params):
    for func_karg_key, _ in considered_params.items():
        if func_karg_key.endswith("()"):
            func_name = func_karg_key[:-2]
            # param format: func_name()
            for command_data in program_content:
                if func_name == command_data["func_name"]:
                    return True
        else:
            # param format: func_name|karg_key
            if "|" in func_karg_key:
                func_name, karg_key = func_karg_key.split("|")
                for command_data in program_content:
                    if command_data["func_name"] == func_name and karg_key in command_data["kargs"]:
                        return True
    return False

if __name__ == "__main__":

    universal_dir = "data/universal"
    counting_dir = "data/counting"
    mapping_dir = "data/mapping_when_permitted"
    output_dir = "data/result_analysis_attributes_when_permitted"
    all_results = None
    for dataset_name in ["Matplotlib_Notebook",
                         "Matplotlib_Python",
                         "PlotCoder_Matplotlib_Python",
                         "ChartDialog_Matplotlib_Python"]:
        
        result = main_count_attributes_when_permitted(counting_dir=counting_dir,
                                                universal_dir=universal_dir, 
                                                mapping_dir=mapping_dir, 
                                                dataset_name=dataset_name, 
                                                verbose=True)
        if all_results is None:
            all_results = result
        else:
            for k, v in result.items():
                all_results[k].update(v)
    
    # Save the result
    os.makedirs(output_dir, exist_ok=True)
    with open(f"{output_dir}/summary_stats_percentage.tsv", "w", encoding="utf-8") as fo:
        fo.write(f"Category\tAttribute\tMatplotlib_Python\tMatplotlib_Notebook\tPlotCoder_Matplotlib_Python\tChartDialog_Matplotlib_Python\n")
        for cat_att, dataset_values in all_results.items():
            category, attribute = cat_att
            fo.write(f"{category}\t{attribute}\t{dataset_values['Matplotlib_Python']}\t{dataset_values['Matplotlib_Notebook']}\t{dataset_values['PlotCoder_Matplotlib_Python']}\t{dataset_values['ChartDialog_Matplotlib_Python']}\n")

    


        
        