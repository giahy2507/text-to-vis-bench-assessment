import os
import json
import tqdm
from collections import defaultdict
from pprint import pprint
from counting_plottype_python_condition import all_list_conditions_2nd_version, plot_func_conditions_dict


def check_usage(json_data, condition_args=None, condition_kargs=None):
    # comparing non-keyword arguments --> try to reject (return false)
    if condition_args:
        # different number of arguments --> reject
        if len(json_data["args"]) != len(condition_args):
            return False
        
        # comparing each argument
        for arg, c_arg in zip(json_data["args"], condition_args):
            # if the condition is "Any", we skip the comparison
            if c_arg == "Any":
                continue
            
            # if the condition is "<class>" --> reject if c_arg and arg are not the same
            # "<class>" mean, this argument is assigned by a variable name. 
            # The parser cannot extract the value of this variable
            if isinstance(c_arg, str):
                if c_arg.startswith("<class") and c_arg.endswith(">"):
                    if isinstance(arg, str):
                        if arg.startswith("<class") and arg.endswith(">"):
                            continue
                        else:
                            return False
                    else:
                        return False
            
            # if the condition is a list, we need to check if the argument is in the list
            elif isinstance(c_arg, list):
                # we are considering special case, not a variable name
                if str(arg).startswith("<class") and str(arg).endswith(">"):
                    return False
                
                # handling operator located in the first element of the list
                if len(c_arg) == 0:
                    continue
                else:
                    operator = True
                    if c_arg[0] == "!NOT":
                        operator = False
                        c_arg = c_arg[1:]
                # handling with operator
                if operator:  
                    # in "operator"
                    flag = False
                    for code in c_arg:
                        if (code in str(arg).strip("\"")):
                            flag = True
                else:
                    # not in "operator"
                    flag = True
                    for code in c_arg:
                        if (code in str(arg).strip("\"")):
                            flag = False
                if flag is True:
                    continue
                else:
                    return False
                
            else:
                # general comparison
                if str(arg) != str(c_arg):
                    return False
                
    # comparing keyword arguments --> try to reject (return false)
    if condition_kargs:
        for c_key, c_value in condition_kargs.items():
            # "c_value (condition value) is None" means that the key_name must not be in the json_data["kargs"]
            # For example: {"linestyle": None} --> the "linestyle" karg should not be in "plot()"
            if c_value is None:
                if c_key in json_data["kargs"]:
                    return False
            else:
                if c_key not in json_data["kargs"]:
                    return False
                else:
                    if c_value == "Any":
                        continue 
                    else:
                        for value in json_data["kargs"][c_key]:
                            if str(value).strip("\"") != str(c_value).strip("\""):
                                return False
    return True
    
    
def check_usage_OR_condition_list(json_data, func_name, condition_list):
    # Check if the function name is the same (e.g., plot, scatter, bar, etc.)
    if func_name == json_data["func_name"]:
        if len(condition_list) == 0:
            # If there is no condition, return True. This is for bar(), barh(), hist(), pie(), contour(), contourf(), streamplot()
            return True
        else:
            # plot() can either visualise scatter and line plot - we need conditions to distinguish them
            # imgshow() can visualise heatmap and image - we need conditions to distinguish them
            for condition_args, condition_kargs in condition_list:
                check_result = check_usage(json_data, condition_args, condition_kargs)
                if check_result is True:
                    return True
            return False
    else:
        return False


def main_count_matplotlib_based(jsonl_path, target_lib):
    for func_name, condition_name_list in plot_func_conditions_dict.items():
        
        counter_dict = defaultdict(int)
        with open(jsonl_path, mode="r", encoding="utf-8") as fi:
            for line in tqdm.tqdm(fi, leave=False):
                # each line is a program
                for json_data in json.loads(line.strip())["content"]:
                    # each json_data is a function call
                    if json_data["target_lib"] != target_lib:
                        continue
                    
                    for condition_name in condition_name_list:
                        condition_list = all_list_conditions_2nd_version[condition_name]
                        check_flag = check_usage_OR_condition_list(json_data, func_name, condition_list)
                        if check_flag:
                            counter_dict[condition_name] += 1
        print(func_name)
        pprint(counter_dict)
        print("------"*10)        


if __name__ == "__main__":
    jsonl_path = "data/universal/Matplotlib_Python.universal2.jsonl"
    print("Matplotlib_Python")
    main_count_matplotlib_based(jsonl_path=jsonl_path, target_lib="matplotlib")

    jsonl_path = "data/universal/Matplotlib_Notebook.universal2.jsonl"
    print("Matplotlib_Notebook")
    main_count_matplotlib_based(jsonl_path=jsonl_path, target_lib="matplotlib")

    jsonl_path = "data/universal/PlotCoder_Matplotlib_Python.universal2.jsonl"
    print("PlotCoder_Matplotlib_Python")
    main_count_matplotlib_based(jsonl_path=jsonl_path, target_lib="matplotlib")

    jsonl_path = "data/universal/ChartDialog_Matplotlib_Python.universal2.jsonl"
    print("ChartDialog_Matplotlib_Python")
    main_count_matplotlib_based(jsonl_path=jsonl_path, target_lib="chartdialog")
        
    


