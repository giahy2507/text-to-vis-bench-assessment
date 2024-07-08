import os
import json
import tqdm
from collections import defaultdict
from pprint import pprint


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
                if func_name in ["mark"]:
                    for karg, karg_values in json_data["kargs"].items():
                        if karg == "mark" or karg == "type":
                            counter_dict["# line"] += karg_values.count("line")
                            counter_dict["# scatter"] += karg_values.count("point")
                            counter_dict["# scatter"] += karg_values.count("circle")
                            counter_dict["# bar"] += karg_values.count("bar")
                            counter_dict["# pie"] += karg_values.count("arc")
    print(func_name)
    pprint(counter_dict)
    print("------"*10)


if __name__ == "__main__":
    jsonl_path = "data/universal/Vegalite_Vega.universal2.jsonl"
    print("Vegalite_Vega")
    main_counting(jsonl_path=jsonl_path, target_lib="vega-lite")

    jsonl_path = "data/universal/nvBench_Vegalite_Vega.universal2.jsonl"
    print("nvBench_Vegalite_Vega")
    main_counting(jsonl_path=jsonl_path, target_lib="vega-lite")

        
    


