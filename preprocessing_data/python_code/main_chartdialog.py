import glob
import json
from collections import OrderedDict, defaultdict
from pprint import pprint
from tqdm import tqdm
import os



plot_type_mapping_dict = {
        "bar plot": "bar",
        "histogram": "hist",
        "line chart": "plot",
        "scatter plot": "scatter",
        "pie chart": "pie",
        "contour plot": "contour",
        "matrix display": "imshow",
        "streamline plot": "streamplot",
    }

def main_convert_to_universal_2():
    verbose = False

    # Download ChartDialog dataset from 
    # https://drive.usercontent.google.com/download?id=1B8tKdmI3LlAMsPQQW6KsCbTKfsm9vnFA&export=download&authuser=0
    # and save as "data/raw-data/ChartDialog"
    chartdialog_dir = "data/raw-data/ChartDialog"
    paths = sorted(glob.glob(f"{chartdialog_dir}/dialogs/*.json"))

    # output
    output_file_path = "data/universal/ChartDialog_Matplotlib_Python.universal2.jsonl"
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    fo = open(output_file_path, mode="w", encoding="utf-8")

    # parsing
    for path in tqdm(paths):
        universal_items = []
        all_slot_dict = []
        values_dict = OrderedDict()
        
        json_data = json.load(open(path, mode="r", encoding="utf-8"))

        # handling slot-filling data
        for i, turn in enumerate(json_data["data"]):
            for utterance in turn["utterances"]:
                plotting_params = utterance.get("plotting_params", None)
                if not plotting_params:
                    continue
                
                slot_dict = OrderedDict()
                for key, value in plotting_params.items():
                    if value is None:
                        continue
                    if key not in values_dict:
                        values_dict[key] = []
                    if len(values_dict[key]) == 0:
                        values_dict[key].append(value)
                        slot_dict[key] = value
                    else:
                        if value != values_dict[key][-1]:
                            values_dict[key].append(value)
                            slot_dict[key] = value
                all_slot_dict.append(slot_dict)
        
        # ------------------------------------
        current_plot_type = None
        for slot_dict in all_slot_dict:
            if "plot_type" in slot_dict:
                if current_plot_type != None:
                    if current_plot_type != slot_dict["plot_type"]:
                        print("ERROR: current_plot_type != slot_dict[plot_type]")
                current_plot_type = slot_dict["plot_type"]
            if current_plot_type is None:
                continue
            
            chart_func = plot_type_mapping_dict.get(current_plot_type, None)
            if chart_func is None:
                continue

            universal_item = {
                "var_call": "chartdialog",
                "target_lib": "chartdialog",
                "args": [],
                "func_name": chart_func,
                "kargs": {}
            }
            for key, value in slot_dict.items():
                if key == "plot_type":
                    continue
                if value:
                    if key not in universal_item["kargs"]:
                        universal_item["kargs"][key] = [value]
            universal_items.append(universal_item)

        if verbose:
            for item in universal_items:
                pprint(item)
            print("-"*50)


        file_id = os.path.basename(path)
        fo.write(json.dumps({
            "file_id": file_id,
            "content": universal_items
        }, ensure_ascii=False) + "\n")

    fo.close()


if __name__ == "__main__":
    main_convert_to_universal_2()

    


            
        
    

    

                
