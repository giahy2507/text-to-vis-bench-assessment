import os
import json
import tqdm
from collections import defaultdict
from pprint import pprint

all_list_conditions_2nd_version_chartjs = {
    "# no condition": [],
    "# line": [
        (None, {"type": "line"}),
    ],
    "# scatter": [
        (None, {"type": "scatter"}),
        (None, {"type": "bubble"}),
    ],
    "# bar": [
        (None, {"type": "bar"}),
    ],
    "# pie": [
        (None, {"type": "pie"}),
    ]
}

plot_func_conditions_dict_chartjs = {
    "type": ["# line", "# scatter", "# bar", "# pie"],
    "data|datasets": ["# line", "# scatter", "# bar", "# pie"],
}

def main_counting(jsonl_path, target_lib):
    counter_dict = defaultdict(int)
    with open(jsonl_path, mode="r", encoding="utf-8") as fi:
        for line in tqdm.tqdm(fi, leave=False):
            # each line is a program
            for json_data in json.loads(line.strip())["content"]:
                # each json_data is a function call
                if json_data["target_lib"] != target_lib:
                    continue
                
                func_name = json_data["func_name"]
                if func_name in ["type", "data|datasets"]:
                    for karg, karg_values in json_data["kargs"].items():
                        if karg == "type":
                            counter_dict["# line"] += karg_values.count("line")
                            counter_dict["# scatter"] += karg_values.count("scatter")
                            counter_dict["# scatter"] += karg_values.count("bubble")
                            counter_dict["# bar"] += karg_values.count("bar")
                            counter_dict["# pie"] += karg_values.count("pie")
    print(func_name)
    pprint(counter_dict)
    print("------"*10)


if __name__ == "__main__":
    jsonl_path = "data/universal/ChartJS_JavaScript.universal2.jsonl"
    print("ChartJS_JavaScript")
    main_counting(jsonl_path=jsonl_path, target_lib="chartjs")

        
    


