import json
import os
from openpyxl import load_workbook
from collections import defaultdict


def handle_params_value(value):
    if value is None:
        return []
    elif str(value).lower() == "not found":
        return []
    else:
        params = value.strip().split("\n")
        params = [param.strip() for param in params]
        return params
    
def handle_default_value(value):
    if value is None:
        return ["NotAssign"] 
    elif str(value).lower() == "not found":
        return ["NotAssign"]
    else:
        if str(value).find("\n") == -1:
            return [str(value).strip()]
        else:
            values = value.strip().split("\n")
            return [v.strip() for v in values]

def handle_default_value_level(value):
    if str(value).lower() == "command":
        return "Command"
    else:
        return "Program"

def try_convert_number(number_str: str):
    try:
        return float(number_str)
    except:
        return number_str

def build_default_values_dict(params, default_values):
    result = defaultdict(list)
    if len(default_values) == 1:
        if default_values[0] == "NotAssign":
            assigned_value = "notassign"
        else:
            assigned_value = default_values[0]
            assigned_value = assigned_value.strip().strip("\"").strip("\'").strip().lower()
        for param in params:
            if assigned_value != "notassign":
                result[param].append(assigned_value)
            else:
                result[param] = []
    else:
        if "=" in default_values[0]:
            for default_value in default_values:
                key, value = default_value.rsplit("=", maxsplit=1)
                assigned_value = value.strip().strip("\"").strip("\'").strip().lower()
                if assigned_value != "notassign":
                    result[key.strip()].append(assigned_value)
        else:
            for param in params:
                for d_value in default_values:
                    assigned_value = d_value.strip().strip("\"").strip("\'").strip().lower()
                    if assigned_value != "notassign":
                        result[param].append(assigned_value)
    return result


def load_default_attribute_dict(mapping_xlsx_path, dataset_name):
    xlsx_path = mapping_xlsx_path
    wb = load_workbook(filename=xlsx_path, read_only=True)
    ws = wb['Annotation']

    rows = ws.rows
    all_default_attributes_dict = []
    for i, row in enumerate(rows):
        if i == 0:
            continue
        if len(row) == 0:
            continue
        if row[0].value is None:
            continue
        category = row[0].value
        attribute = row[1].value
        if dataset_name == "Matplotlib_Python":
            row_list = [2,3,4]
        elif dataset_name == "Graphics_R":
            row_list = [5,6,7]
        elif dataset_name == "ChartJS_JavaScript":
            row_list = [8,9,10]
        elif dataset_name == "Vegalite_Vega":
            row_list = [11,12,13]
        elif dataset_name == "ChartDialog_Matplotlib_Python":
            row_list = [14, 15, 16]
        else:
            raise ValueError("Not support dataset name!")
        
        params = handle_params_value(row[row_list[0]].value)
        params_default_values = handle_default_value(row[row_list[1]].value)
        params_affecting_level = handle_default_value_level(row[row_list[2]].value)
        default_params_dict = build_default_values_dict(params, params_default_values)
        all_default_attributes_dict.append({"category": category, 
                                        "attribute": attribute, 
                                        "affecting_level": params_affecting_level, 
                                        "params_with_default_values": default_params_dict})
        
    return all_default_attributes_dict

def main_export_default_values(mapping_dir):
    mapping_xlsx_path = f"{mapping_dir}/Cross-language Mappings - Values Investigation.xlsx"

    datasets_name = ["Matplotlib_Notebook",
                     "Matplotlib_Python", 
                     "PlotCoder_Matplotlib_Python",
                     "ChartDialog_Matplotlib_Python",
                     "Graphics_R", 
                     "ChartJS_JavaScript", 
                     "Vegalite_Vega",
                     "nvBench_Vegalite_Vega"]
    
    for dataset_name in datasets_name:
        
        dataset_name_4_params = dataset_name
        if dataset_name == "PlotCoder_Matplotlib_Python" or dataset_name == "Matplotlib_Notebook":
            dataset_name_4_params = "Matplotlib_Python"
        elif dataset_name == "nvBench_Vegalite_Vega":
            dataset_name_4_params = "Vegalite_Vega"

        all_default_attributes_dict = load_default_attribute_dict(mapping_xlsx_path=mapping_xlsx_path, 
                                                                  dataset_name=dataset_name_4_params)
        
        with open(f"{mapping_dir}/attributes/{dataset_name}.json", mode="w", encoding="utf-8") as fo:
            json.dump(all_default_attributes_dict, fo, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    mapping_permitted_dir = "data/mapping_when_permitted"
    main_export_default_values(mapping_permitted_dir)