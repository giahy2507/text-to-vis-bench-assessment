import json
import csv
import os
from pprint import pprint
from openpyxl import load_workbook
from collections import OrderedDict, defaultdict


def handle_value(value):
    if value is None:
        return []
    elif str(value).lower() == "not found":
        return []
    else:
        params = value.strip().split("\n")
        return params
    
def convert_mapping_xlsx_to_json(mapping_dir):
    mappings_xlsx_path = f"{mapping_dir}/Cross-language Mappings.xlsx"
    wb = load_workbook(filename=mappings_xlsx_path, read_only=True)
    ws = wb['Cross-Language-Mapping-Ver1']

    rows = ws.rows
    data = []
    for i, row in enumerate(rows):
        if i == 0:
            continue
        if len(row) == 0:
            continue
        if row[0].value is None:
            continue
        category = row[0].value
        attribute = row[1].value
        python_params = handle_value(row[2].value)
        r_params = handle_value(row[3].value)
        chartjs_params = handle_value(row[4].value)
        vegalite_params = handle_value(row[5].value)
        chartdialog_params = handle_value(row[6].value)
        data.append({
            "Category": category,
            "Attribute": attribute,
            "Matplotlib_Python": python_params,
            "Matplotlib_Notebook": python_params,
            "Graphics_R": r_params,
            "ChartJS_JavaScript": chartjs_params,
            "Vegalite_Vega": vegalite_params,
            "NLVCorpus_Vegalite_Vega": vegalite_params,
            "ChartDialog_Matplotlib_Python": chartdialog_params
        })

    mappings_json_path = mappings_xlsx_path.replace(".xlsx", ".json")
    with open(mappings_json_path, "w", encoding="utf-8") as fo:
        json.dump(data, fo, indent=4, ensure_ascii=False)

def load_tsv_file(tsv_path, topk=None, return_dict=False):
    """
    load tsv file using csv lib
    """
    with open(tsv_path, "r", encoding="utf-8") as fi:
        reader = csv.reader(fi, delimiter="\t")
        data = []
        for row in reader:
            data.append(row)
    if topk:
        data = data[: min(topk, len(data))]
    if return_dict:
        data = {row[0]: row[1] for row in data[1:]}
    return data

def count_frequency_over_dataset(dataset_name, 
                            mapping_dir,
                            counting_dir,
                            special_cases_path,
                            verbose=False):

    # Counting of special cases, such as "plt.axis('off')", "spines['top'].set_visible", ...
    special_cases = load_tsv_file(special_cases_path, return_dict=False)

    # Loading mappings
    mapping_json_path = f"{mapping_dir}/Cross-language Mappings.json"
    mapping_items = json.load(open(mapping_json_path, "r", encoding="utf-8"))
    freq_dict = OrderedDict()
    no_freq_dict = defaultdict(list)
    
    # Loading dataset counting for function and kargs
    tsv_stats_func_path = f"{counting_dir}/{dataset_name}/top_all_func.tsv"
    dataset_stats_func = load_tsv_file(tsv_stats_func_path, return_dict=True)
    tsv_stats_args_path = f"{counting_dir}/{dataset_name}/top_all_func_args.tsv"
    dataset_stats_args = load_tsv_file(tsv_stats_args_path, return_dict=True)

    for mapping_item in mapping_items:
        category = mapping_item["Category"]
        attribute = mapping_item["Attribute"]

        # handling similar dataset
        dataset_name_4_params = dataset_name
        if dataset_name == "PlotCoder_Matplotlib_Python":
            dataset_name_4_params = "Matplotlib_Python"
        elif dataset_name == "nvBench_Vegalite_Vega":
            dataset_name_4_params = "Vegalite_Vega"
        
        dataset_params = mapping_item[dataset_name_4_params]
        counter = 0
        for param in dataset_params:
            param = param.strip()

            # Handling special cases
            special_case = find_in_special_cases(special_cases, dataset_name, param)
            if special_case != None:
                # print("Special Cases: ", dataset_name, param, special_case)
                counter+=int(special_case)
                continue

            # Handling "func|karg"
            if param in dataset_stats_args:
                counter+=int(dataset_stats_args[param])
            else:
                # Handling func which marked as "xxx()"
                if param.endswith("()"):
                    func_param = param[:-2]
                    if func_param in dataset_stats_func:
                        counter+=int(dataset_stats_func[func_param])
                else:
                    no_freq_dict[f"{category}_{attribute}"].append(param)

        freq_dict[f"{category}_{attribute}"] = counter

    if verbose:
        for cat_att, value in freq_dict.items():
            print(f"{cat_att}\t{dataset_name}\t{value}\t{no_freq_dict[cat_att]}")
    
    return freq_dict


def find_in_special_cases(special_cases, dataset_name, arg_param):
    for item in special_cases:
        if item[0] == dataset_name and item[1] == arg_param:
            return item[2]
    return None


def main_count_freq_attributes(mapping_dir, counting_dir, special_cases_path, output_dir, verbose=False):
    
    datasets_name = ["Matplotlib_Notebook",
                     "Matplotlib_Python", 
                     "PlotCoder_Matplotlib_Python",
                     "ChartDialog_Matplotlib_Python",
                     "Graphics_R", 
                     "ChartJS_JavaScript", 
                     "Vegalite_Vega",
                     "nvBench_Vegalite_Vega"]

    datasets_stats = []
    for dataset_name in datasets_name:
        stats = count_frequency_over_dataset(dataset_name=dataset_name,
                                        mapping_dir=mapping_dir,
                                        counting_dir=counting_dir,
                                        special_cases_path=special_cases_path,
                                        verbose=verbose)
        datasets_stats.append(stats)

    counter_dataset_dict = defaultdict(int)    
    with open(f"{output_dir}/summary_stats_freq.tsv", "w", encoding="utf-8") as fo:
        fo.write(f"Category\tAttribute\t{datasets_name[0]}\t{datasets_name[1]}\t{datasets_name[2]}\t{datasets_name[3]}\t{datasets_name[4]}\t{datasets_name[5]}\t{datasets_name[6]}\t{datasets_name[7]}\n")
        params = datasets_stats[0].keys()
        for cat_att in params:
            category, attribute = cat_att.split("_")
            counter = []
            for dataset_name, dataset_stats in zip(datasets_name, datasets_stats):
                counter.append(dataset_stats[cat_att])
                counter_dataset_dict[dataset_name]+=dataset_stats[cat_att]
            fo.write(f"{category}\t{attribute}\t{counter[0]}\t{counter[1]}\t{counter[2]}\t{counter[3]}\t{counter[4]}\t{counter[5]}\t{counter[6]}\t{counter[7]}\n")

    if verbose:
        pprint(counter_dataset_dict)
    with open(f"{output_dir}/summary_stats_percentage.tsv", "w", encoding="utf-8") as fo:
        fo.write(f"Category\tAttribute\t{datasets_name[0]}\t{datasets_name[1]}\t{datasets_name[2]}\t{datasets_name[3]}\t{datasets_name[4]}\t{datasets_name[5]}\t{datasets_name[6]}\t{datasets_name[7]}\n")
        params = datasets_stats[0].keys()
        for cat_att in params:
            category, attribute = cat_att.split("_")
            counter = []
            for dataset_name, dataset_stats in zip(datasets_name, datasets_stats):
                percent = (dataset_stats[cat_att]/counter_dataset_dict[dataset_name])*100
                counter.append(f"{percent:.4f}")
            fo.write(f"{category}\t{attribute}\t{counter[0]}\t{counter[1]}\t{counter[2]}\t{counter[3]}\t{counter[4]}\t{counter[5]}\t{counter[6]}\t{counter[7]}\n")


if __name__ == "__main__":
    universal_dir = "data/universal"
    mapping_dir = "data/mapping"
    counting_dir = "data/counting"
    special_cases_path = f"{universal_dir}/special_cases.tsv"
    output_dir = "data/result_analysis_attributes"
    os.makedirs(output_dir, exist_ok=True)

    convert_mapping_xlsx_to_json(mapping_dir=mapping_dir)
    main_count_freq_attributes(mapping_dir=mapping_dir, 
                               counting_dir=counting_dir, 
                               special_cases_path=special_cases_path,
                               output_dir=output_dir, 
                               verbose=False)

    

    


    
    
                




        
    
        