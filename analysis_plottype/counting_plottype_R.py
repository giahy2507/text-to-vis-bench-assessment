import os
import json
import tqdm
from collections import defaultdict
from pprint import pprint

from counting_plottype_python import check_usage_OR_condition_list

all_list_conditions_2nd_version_R = {
    "# no condition": [],
    # condition for lines
    "# plot() line graph" : [
        (None, {"type": "l"}),
        (None, {"type": "b"}),
        (None, {"type": "c"}),
        (None, {"type": "o"}),
        (None, {"lwd": "Any"}),
        (None, {"lty": "Any"}),
    ],
    "# plot() line graph exception" : [
        (None, {"lty": "blank"}),
        (None, {"lwd": "0"}),
    ],
    "# plot() plot nothing": [
        (None, {"type": "n"}),
    ]
}

plot_func_conditions_dict_R = {
    "lines": ["# no condition"],
    "plot": ["# no condition", "# plot() line graph", "# plot() line graph exception", "# plot() plot nothing"],
    "points": ["# no condition"],
    "barplot": ["# no condition"],
    "hist": ["# no condition"],
    "pie": ["# no condition"],
    "contour": ["# no condition"],
}

def main_count_matplotlib_based(jsonl_path, target_lib):
    for func_name, condition_name_list in plot_func_conditions_dict_R.items():
        counter_dict = defaultdict(int)
        with open(jsonl_path, mode="r", encoding="utf-8") as fi:
            for line in tqdm.tqdm(fi, leave=False):
                # each line is a program
                for json_data in json.loads(line.strip())["content"]:
                    # each json_data is a function call
                    if json_data["target_lib"] != target_lib:
                        continue
                    
                    for condition_name in condition_name_list:
                        condition_list = all_list_conditions_2nd_version_R[condition_name]
                        check_flag = check_usage_OR_condition_list(json_data, func_name, condition_list)
                        if check_flag:
                            counter_dict[condition_name] += 1
        print(func_name)
        pprint(counter_dict)
        print("------"*10)


if __name__ == "__main__":
    jsonl_path = "data/universal/Graphics_R.universal2.jsonl"
    print("Graphics_R")
    main_count_matplotlib_based(jsonl_path=jsonl_path, target_lib="graphics")

        
    


