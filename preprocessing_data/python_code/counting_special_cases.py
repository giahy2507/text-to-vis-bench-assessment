import glob
import json
from collections import defaultdict
from tqdm import tqdm
from pprint import pprint

cases_dict = {
    "plt.axis('off')": ["Matplotlib_Python", "file_search"],
    "spines['top'].set_visible": ["Matplotlib_Python", "file_search"],
    "spines['right'].set_visible": ["Matplotlib_Python", "file_search"],
    "spines['bottom'].set_visible": ["Matplotlib_Python", "file_search"],
    "spines['left'].set_visible": ["Matplotlib_Python", "file_search"],

    "options|indexAxis=y": ["ChartJS_JavaScript", "value_search"],
    "mark|orient=horizontal": ["Vegalite_Vega", "value_search"],
    "bar|bar_orientation=horizontal": ["ChartDialog_Matplotlib_Python", "value_search"],

    "repeat": ["Vegalite_Vega", "json_file_search"],
    "facet": ["Vegalite_Vega", "json_file_search"],
    "concat": ["Vegalite_Vega", "json_file_search"],
    "hconcat": ["Vegalite_Vega", "json_file_search"],
    "vconcat": ["Vegalite_Vega", "json_file_search"],
    # "layer": ["Vegalite_Vega", "json_file_search"],
}


def get_universal_paths(dataset_name, dataset_dir):
    # Github code
    if dataset_name == "Matplotlib_Python":
        paths = glob.glob(f"{dataset_dir}/Matplotlib_Python/Python_matplotlib_all.universal.jsonl")
    else:
        raise ValueError("Invalid dataset!")
    paths = sorted(paths)
    return paths

def main_search_python():
    # python
    path = "/Users/nngu0448/Documents/data/the-stack/Python/matplotlib.jsonl"

    # plotcoder
    path = "/Users/nngu0448/Documents/data/juice/juice-dataset/all.code.jsonl"

    # jupyter notebook
    path = "/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-2/Matplotlib_Notebook/Jupyter_Notebook.matplotlib.jsonl"

    counter_dict = defaultdict(int)
    with open(path, mode="r", encoding="utf-8") as fi:
        for line in tqdm(fi):
            json_data = json.loads(line)
            content = json_data["content"]
            if "plt.axis('off')" in content:
                counter_dict["plt.axis('off')"]+=1
            if "spines['top'].set_visible" in content:
                counter_dict["spines['top'].set_visible"]+=1
            if "spines['right'].set_visible" in content:
                counter_dict["spines['right'].set_visible"]+=1
            if "spines['bottom'].set_visible" in content:
                counter_dict["spines['bottom'].set_visible"]+=1
            if "spines['left'].set_visible" in content:
                counter_dict["spines['left'].set_visible"]+=1
    pprint(counter_dict)

def main_search_vegalite():
    from Vegalite_code.main import extract_vega_lite_component
    dataset_dir = "/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-1"
    counter_dict = defaultdict(int)
    # vegalite
    paths = []
    # paths += glob.glob(f"{dataset_dir}/Vegalite_Vega/Vega-lite/JSON/JSON_Versionized/*/*.json")
    # paths += glob.glob(f"{dataset_dir}/Vegalite_Vega/Vega-lite/JavaScript/JS-vegalite-versionized/*/*.json")

    paths += glob.glob(f"{dataset_dir}/nvBench_Vegalite_Vega/nvBench_VegaLite_js/*.vega-lite.json")
    for vegalite_path in paths:
        vegalite_items = extract_vega_lite_component(vegalite_path)
        for i, vegalite_item in enumerate(vegalite_items):
            if "repeat" in vegalite_item:
                counter_dict["repeat"]+=1
            if "facet" in vegalite_item:
                counter_dict["facet"]+=1
            if "concat" in vegalite_item:
                counter_dict["concat"]+=1
            if "hconcat" in vegalite_item:
                counter_dict["hconcat"]+=1
            if "vconcat" in vegalite_item:
                counter_dict["vconcat"]+=1
    pprint(counter_dict)

def counting_param_with_value():
    from counting_universal import get_universal_paths
    dataset_dir = "/Users/nngu0448/Documents/data/code-gen-4-vis-phase-1/Universal-Usage-1"
    value_search_dict = {
        "ChartJS_JavaScript": ["options|indexAxis=y"],
        "Vegalite_Vega": ["mark|orient=horizontal"],
        "ChartDialog_Matplotlib_Python": ["bar|bar_orientation=horizontal"]
    }
    counter_dict = defaultdict(int)
    for dataset_name, key_list in value_search_dict.items():
        paths = get_universal_paths(dataset_name, dataset_dir)
        for key in key_list:
            func_arg_name, value = key.split("=")
            func_name, arg_name = func_arg_name.split("|")
            for path in paths:
                with open(path, mode="r", encoding="utf-8") as fi:
                    for line in tqdm(fi, leave=False):
                        json_data = json.loads(line)
                        if func_name == json_data["func_name"]:
                            if arg_name in json_data["kargs"]:
                                for _value, default_value in json_data["kargs"][arg_name]:
                                    if str(value).strip() == str(_value).strip():
                                        counter_dict[key]+=1
                                        break
    print(counter_dict)

if __name__ == "__main__":
    main_search_python()
        
    

