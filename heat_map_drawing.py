from openpyxl import load_workbook
import json
import csv
import os
from pprint import pprint
from collections import OrderedDict, defaultdict
from sklearn.preprocessing import minmax_scale
import numpy as np


def handle_value(value):
    if value is None:
        return []
    elif str(value).lower() == "not found":
        return []
    else:
        params = value.strip().split("\n")
        return params
    
def convert_mapping_xlsx_to_json():
    xlsx_path = '/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-2/Mapping_Summary/Plotting-Params-Summary.xlsx'
    wb = load_workbook(filename=xlsx_path, read_only=True)
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

    json_path = xlsx_path.replace(".xlsx", ".json")
    with open(json_path, "w", encoding="utf-8") as fo:
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

def count_following_summary(dataset_name="Matplotlib_Python", 
                            verbose=False,
                            stats_version = "Counting-v1.2.4"
                            ):
    special_cases = load_tsv_file("/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-2/Mapping_Summary/special_cases.tsv",
                                  return_dict=False)
    data_dir = "/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-2"
    json_path = f"{data_dir}/Mapping_Summary/Plotting-Params-Summary.json"
    summary_items = json.load(open(json_path, "r", encoding="utf-8"))
    freq_dict = OrderedDict()
    no_freq_dict = defaultdict(list)
    
    # load dataset counting
    tsv_stats_func_path = f"{data_dir}/{dataset_name}/{stats_version}/top_all_func.tsv"
    dataset_stats_func = load_tsv_file(tsv_stats_func_path, return_dict=True)
    tsv_stats_args_path = f"{data_dir}/{dataset_name}/{stats_version}/top_all_func_args.tsv"
    dataset_stats_args = load_tsv_file(tsv_stats_args_path, return_dict=True)

    for summary_item in summary_items:
        category = summary_item["Category"]
        attribute = summary_item["Attribute"]

        dataset_name_4_params = dataset_name
        if dataset_name == "PlotCoder_Matplotlib_Python":
            dataset_name_4_params = "Matplotlib_Python"
        elif dataset_name == "nvBench_Vegalite_Vega":
            dataset_name_4_params = "Vegalite_Vega"
        
        dataset_params = summary_item[dataset_name_4_params]
        sum_freq = 0
        for param in dataset_params:
            param = param.strip()
            # Handling special cases
            special_case = find_in_special_cases(special_cases, dataset_name, param)
            if special_case != None:
                # print("Special Cases: ", dataset_name, param, special_case)
                sum_freq+=int(special_case)
                continue
            # Handling func|karg
            if param in dataset_stats_args:
                sum_freq+=int(dataset_stats_args[param])
            else:
                # Handling func
                if param.endswith("()"):
                    func_param = param[:-2]
                    if func_param in dataset_stats_func:
                        sum_freq+=int(dataset_stats_func[func_param])
                else:
                    no_freq_dict[f"{category}_{attribute}"].append(param)

        freq_dict[f"{category}_{attribute}"] = sum_freq

    if verbose:
        for cat_att, value in freq_dict.items():
            print(f"{cat_att}\t{dataset_name}\t{value}\t{no_freq_dict[cat_att]}")
    
    return freq_dict


def find_in_special_cases(special_cases, dataset_name, arg_param):
    for item in special_cases:
        if item[0] == dataset_name and item[1] == arg_param:
            return item[2]
    return None


def main_count_freq(stats_version = "Counting-v1.2.4"):
    # Need counting for special cases first
    # Look: "counting_special_cases.py"
    # Look: "python_code/counting_plottype_python.py" to run "all_list_conditions_3"
    datasets_name = ["Matplotlib_Notebook",
                     "Matplotlib_Python", 
                     "PlotCoder_Matplotlib_Python",
                     "ChartDialog_Matplotlib_Python",
                     "Graphics_R", 
                     "ChartJS_JavaScript", 
                     "Vegalite_Vega",
                     "nvBench_Vegalite_Vega",
                     "NLVCorpus_Vegalite_Vega"]
    
    convert_mapping_xlsx_to_json()

    datasets_stats = []
    for dataset_name in datasets_name:
        stats = count_following_summary(dataset_name=dataset_name, 
                                        verbose=True,
                                        stats_version=stats_version)
        datasets_stats.append(stats)
        # print("-"*100)
    
    counter_dataset_dict = defaultdict(int)
    dir_path = f"/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-2/Mapping_Summary/{stats_version}"
    os.makedirs(dir_path, exist_ok=True)
    with open(f"{dir_path}/summary_stats_freq.tsv", "w", encoding="utf-8") as fo:
        fo.write(f"Category\tAttribute\t{datasets_name[0]}\t{datasets_name[1]}\t{datasets_name[2]}\t{datasets_name[3]}\t{datasets_name[4]}\t{datasets_name[5]}\t{datasets_name[6]}\t{datasets_name[7]}\t{datasets_name[8]}\n")
        params = datasets_stats[0].keys()
        for cat_att in params:
            category, attribute = cat_att.split("_")
            counter = []
            for dataset_name, dataset_stats in zip(datasets_name, datasets_stats):
                counter.append(dataset_stats[cat_att])
                counter_dataset_dict[dataset_name]+=dataset_stats[cat_att]
            fo.write(f"{category}\t{attribute}\t{counter[0]}\t{counter[1]}\t{counter[2]}\t{counter[3]}\t{counter[4]}\t{counter[5]}\t{counter[6]}\t{counter[7]}\t{counter[8]}\n")

    pprint(counter_dataset_dict)
    with open(f"{dir_path}/summary_stats_percentage.tsv", "w", encoding="utf-8") as fo:
        fo.write(f"Category\tAttribute\t{datasets_name[0]}\t{datasets_name[1]}\t{datasets_name[2]}\t{datasets_name[3]}\t{datasets_name[4]}\t{datasets_name[5]}\t{datasets_name[6]}\t{datasets_name[7]}\t{datasets_name[8]}\n")
        params = datasets_stats[0].keys()
        for cat_att in params:
            category, attribute = cat_att.split("_")
            counter = []
            for dataset_name, dataset_stats in zip(datasets_name, datasets_stats):
                percent = (dataset_stats[cat_att]/counter_dataset_dict[dataset_name])*100
                counter.append(f"{percent:.4f}")
            fo.write(f"{category}\t{attribute}\t{counter[0]}\t{counter[1]}\t{counter[2]}\t{counter[3]}\t{counter[4]}\t{counter[5]}\t{counter[6]}\t{counter[7]}\t{counter[8]}\n")


category_color_dict = {
        'xy-axis': 'yellow',
        "data-plotting": 'blue',
        "title-subtitle": 'black',
        "legend": 'red',
        # "margin": 'yellow',
        # "subplots": 'cyan',
        "annotation": 'magenta',
        "grid": 'brown',
        "figure-format": 'cyan',
        "other": 'gray'
    }

def data_to_tex_command(first_column, x_pos=0, y_gap=0.5, x_pos_text_extend=0.4, width=2, column_label:str=None, cell_color="green", rotation=None):
    first_column_scaled = minmax_scale(first_column, feature_range=(0, 100), axis=0, copy=True)
    first_column_scaled = first_column_scaled.astype("int32")
    for i, item in enumerate(first_column):
        opacity = first_column_scaled[i]
        print(f"\\fill[{cell_color}!{opacity}!white] ({x_pos:.4f},{i*y_gap:.4f}) rectangle ({x_pos+width:.4f},{i*y_gap+y_gap:.4f});", sep="")
        print("\\node[anchor=south west, inner sep=2, font=\\fontsize{8}{8}\\selectfont]" f" at ({x_pos+x_pos_text_extend:.4f},{i*y_gap:.4f}) "+ "{" + f"{item:.1f}"+ "};", sep="")

    if column_label and column_label != "":
        i = len(first_column)
        if column_label in ["PlotCoder", "ChartDialog", "ChDialog", "nvBench", "NLVCor", "GitHub-T2V", "arXiv-T2V", "OWID-T2V", "GitHub-T2V-Matplotlib", "arXiv-T2V-Matplotlib"]:
            column_label = "\\textcolor{red}{"+ column_label +"}"
        
        if rotation:
            print("\\node[anchor=south west, inner sep=2, rotate=20, yshift=0cm, xshift=0cm ,font=\\fontsize{8}{8}\\selectfont]" + f" at ({x_pos:.4f},{i*y_gap:.4f}) "+ "{\\textbf{" + f"{column_label}"+ "}};", sep="")
        else:
            print("\\node[anchor=south west, inner sep=2, font=\\fontsize{8}{8}\\selectfont]" + f" at ({x_pos:.4f},{i*y_gap:.4f}) "+ "{\\textbf{" + f"{column_label}"+ "}};", sep="")

def text_to_tex_command(first_column, 
                        x_pos=0, 
                        y_gap=0.5, 
                        x_pos_text_extend=0.4, 
                        width=2, 
                        column_label=None,
                        categories=None):
    
    for i, item in enumerate(first_column):
        color = "green"
        if categories:
            category = categories[i]
            color = category_color_dict[category]
        item = item.replace("/", "-")
        print(f"\\fill[{color}!{10}!white] ({x_pos:.4f},{i*y_gap:.4f}) rectangle ({x_pos+width:.4f},{i*y_gap+y_gap:.4f});", sep="")
        print("\\node[anchor=south west, inner sep=2, font=\\fontsize{8}{8}\\selectfont]" + f" at ({x_pos+x_pos_text_extend},{i*y_gap:.4f}) "+ "{" + f"{item}"+ "};", sep="")
    
    if column_label:
        i = len(first_column)
        print("\\node[anchor=south west, inner sep=2, font=\\fontsize{8}{8}\\selectfont]" + f" at ({x_pos+x_pos_text_extend},{i*y_gap:.4f}) "+ "{\\textbf{" + f"{column_label}"+ "}};", sep="")
    

def main_drawing_mapping_heatmap(tsv_path, 
                                 dataset_names, 
                                 color_list= None, 
                                 width_text=5, 
                                 width_cell=2,
                                 data_text_padding_left=0.1,
                                 xaxis_labels_rotation=True):
    if color_list is None:
        color_list = ["green"]*len(dataset_names)

    plotting_data = load_tsv_file(tsv_path)
    categories = [row[0] for row in plotting_data[1:]]
    attribute = [row[1] for row in plotting_data[1:]]
    plotting_data = [row[2:] for row in plotting_data[1:]]

    print(set(categories))
    reversed_plotting_data = []
    reversed_attribute = []
    reversed_categories = []
    for i in range(len(plotting_data)-1, -1, -1):
        reversed_plotting_data.append(plotting_data[i])
        reversed_attribute.append(attribute[i])
        reversed_categories.append(categories[i])
    reversed_plotting_data = np.array(reversed_plotting_data, dtype="float32")

    starting_x_pos = 0
    y_gap = 0.395
    assert len(reversed_attribute) == len(reversed_categories)
    text_to_tex_command(reversed_attribute, 
                        x_pos=starting_x_pos, 
                        y_gap=y_gap, 
                        x_pos_text_extend=0, 
                        width=width_text,
                        column_label="Attribute", 
                        categories=reversed_categories)
    
    for i in range(reversed_plotting_data.shape[1]):
        data_to_tex_command(reversed_plotting_data[:, i], 
                            x_pos=width_cell*(i)+starting_x_pos+width_text, 
                            y_gap=y_gap, 
                            width=width_cell,
                            x_pos_text_extend=data_text_padding_left, 
                            column_label=dataset_names[i],
                            cell_color=color_list[i], rotation=xaxis_labels_rotation)
        print("% +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


if __name__ == "__main__":
    # main_count_freq(stats_version = "Counting-v1.4.0")
    
    dataset_names = ["Matplotlib-nb", "GitHub-T2V", "arXiv-T2V"]
    main_drawing_mapping_heatmap(f"data/result_analysis_attributes_phase2/summary_stats_percentage.tsv", 
                                 dataset_names, 
                                 width_cell=0.75, 
                                 width_text=2.8,
                                 data_text_padding_left=0.1,
                                 xaxis_labels_rotation=True)

    # dataset_names = ["Matplotlib-nb", "DA-T2V", "arXiv-T2V"]
    # color_list = ["orange", "orange", "red", "red"]
    # main_drawing_mapping_heatmap(f"/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-2/Mapping_Summary/Default_Params-v1.4.0/summary_percentage_python_2.tsv",
    #                              dataset_names,
    #                              color_list=color_list,
    #                              width_cell=0.75, 
    #                              width_text=2.8,
    #                              data_text_padding_left=0.1,
    #                              xaxis_labels_rotation=True)

    # dataset_names = ["Matplotlib-nb", "Matplotlib-py", "PlotCoder", "ChDialog", "Graphics", "ChartJS", "VegaLite", "nvBench"]
    # main_drawing_mapping_heatmap(f"/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-2/Mapping_Summary/Counting-v1.4.0/category_stats_percentage.tsv", 
    #                              dataset_names, 
    #                              width_cell=0.75, 
    #                              width_text=2.8,
    #                              data_text_padding_left=0.1,
    #                              xaxis_labels_rotation=True)
    

    


    
    
                




        
    
        