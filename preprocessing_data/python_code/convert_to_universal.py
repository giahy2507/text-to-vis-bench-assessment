import os 
import json
from pprint import pprint
from tqdm import tqdm
import glob
from collections import defaultdict, OrderedDict
from matplotlib_schema_parsing import load_matplotlib_schema


def is_cover_all_required_args(args, kargs, schema_args):
    """
    Checking all required schema_args appearing in args or kargs of func usage
    """
    required_args = [arg_name for arg_name, arg_value in schema_args.items() if arg_value == None]
    for arg in required_args:
        if arg not in args or arg not in kargs:
            return False
    return True

def identify_the_best_func_schema(func_usage, func_schema_list, verbose=False):
    """
    Use "args" and "kargs" in func_usage to identify the best schema list name in func_schema_list
    Args:
        func_usage: 
        func_schema_list: list of matplotlib's functions which has the same name.
            [{
                "class_name: str": "Axes",
                "func_name: str": "plot",
                "args: OrderedDict": {"arg_name": "arg_default_value"}, arg_default_value is None if no default value
                "kargs:OrderedDict": {"karg_name": "karg_default_value"}, karg_default_value is None if no default value
            }]

    """
    func_usage_args = func_usage["args"]
    func_usage_kargs = func_usage["kargs"]
    scores = [0]*len(func_schema_list)
    for i, func_schema in enumerate(func_schema_list):
        
        # Heuristic: -5 for not cover all required args
        if not is_cover_all_required_args(func_usage_args, func_usage_kargs, func_schema["args"]):
            scores[i] -= 5
        
        # Heuristic: +1 for class_name= ["Axes", "_AxesBase"] calling by variable "ax"
        if func_schema["class_name"] in ["Axes", "_AxesBase"] and "var_call" in func_usage:
            if "ax" in str(func_usage["var_call"]) or "plt" in str(func_usage["var_call"]):
                scores[i] +=1

        # Heuristic: +1 for every matched karg
        for karg in func_usage_kargs:
            if karg in func_schema["kargs"]:
                scores[i] +=1
    if verbose:
        for score, func_schema in zip(scores, func_schema_list):
            print("||", score, "||", func_schema)

    the_greatest_score_idx = scores.index(max(scores))
    return func_schema_list[the_greatest_score_idx]


def find_funcname_in_matplotlib_schema(func_usage, matplotlib_schema_dict, verbose=False):
    if "func_name" not in func_usage:
        return None
    
    func_name = func_usage["func_name"]
    for _, version_dict in matplotlib_schema_dict.items():
        if func_name in version_dict:
            # list of possible functions
            if len(version_dict[func_name]) > 1:
                func_schema = identify_the_best_func_schema(func_usage, version_dict[func_name], verbose=verbose)
                return func_schema
            else:
                return version_dict[func_name][0]
    return None

error_dict = defaultdict(int)

def collect_stats_func_usage(func_usage, func_schema):
    stats_func = defaultdict(int)
    stats_func_arg_value = defaultdict(list)
    stats_func_addarg_value = defaultdict(list)
    stats_func_karg_value = defaultdict(list)

    # counting function name
    func_name = func_usage["func_name"]
    stats_func[func_name] +=1

    # please see "extract_node_FunctionDef" in matplotlib_schema.py for more details about schema's args, kargs, add_args, add_kargs
    # Consider the function in the schema has add_args or not
    # in func schema, args --> add_args(*args) --> kargs --> add_kargs (*kwargs)
    # in func usage, args --> kargs

    # Step 1: Handling args
    # Step 1.1: Following order, find keys for func_usage["args"]
    if func_schema["add_args"] is not None:
        # schema_args_kargs_keys is blocked by add_args (*args)
        schema_args_kargs_dict = func_schema["args"]
        schema_args_kargs_keys = list(schema_args_kargs_dict.keys())
    else:
        # schema_args_kargs_keys is not blocked by add_args (*args)
        # we need to consider kargs in the schema as well
        schema_args_kargs_dict = OrderedDict(
                list(func_schema["args"].items()) + list(func_schema["kargs"].items())
            )
        schema_args_kargs_keys = list(schema_args_kargs_dict.keys())

    usage_args = OrderedDict()
    min_length = min(len(func_schema["args"]), len(func_usage["args"]))
    for i in range(min_length):
        arg_name = schema_args_kargs_keys[i]
        usage_args[arg_name] = func_usage["args"][i]

    # Step 1.2: assign default values
    # Assign value for found keys
    for arg_name, arg_value in usage_args.items():
        arg_default = schema_args_kargs_dict[arg_name]
        stats_func_arg_value[f"{func_name}|{arg_name}"].append((arg_value, arg_default))

    # Some time users pass more args than required args
    # If case of passing args to assign kwargs, we will not handle it because we don't know the key name
    # --> add_args
    if len(func_usage["args"]) > len(func_schema["args"]):
        add_agrs = func_usage["args"][min_length:]
        stats_func_addarg_value[f"{func_name}|add_args"].append(add_agrs)
    
    # Step 2: handling kargs: kargs, add_kargs (**kwargs)
    # assign used & default values for kargs
    for karg_name, karg_value in func_usage["kargs"].items():
        if f"{func_name}|{karg_name}" in stats_func_arg_value:
            # prevent overlapping with args
            # for cases, users pass more args than required args
            # schema: func_name(a, b, c=1, d=5)
            # usage : func_name(1, 2, 1, 5) --> already handle above
            continue
        if karg_name in schema_args_kargs_dict:
            karg_default = schema_args_kargs_dict[karg_name]
            stats_func_karg_value[f"{func_name}|{karg_name}"].append((karg_value, karg_default))
        else:
            stats_func_karg_value[f"{func_name}|{karg_name}"].append((karg_value, "Unknown"))
        
    return stats_func, stats_func_arg_value, stats_func_addarg_value, stats_func_karg_value

def convert_to_universal_format(func_usage, matplotlib_schema_dict, universal_version=2, verbose=False):
    func_schema = find_funcname_in_matplotlib_schema(func_usage, matplotlib_schema_dict, verbose=verbose)
    if func_schema:
        stats_func, stats_func_arg_value, stats_func_addarg_value, stats_func_karg_value = collect_stats_func_usage(func_usage, func_schema)
        if verbose:
            print(json.dumps(func_schema))
            print(json.dumps(func_usage))
            print(stats_func)
            print(stats_func_arg_value)
            print(stats_func_addarg_value)
            print(stats_func_karg_value)
        universal_item = {}
        universal_item["var_call"] = func_usage["var_call"]
        universal_item["func_name"] = func_usage["func_name"]
        
        # univeral_args
        if f'{universal_item["func_name"]}|add_args' in stats_func_addarg_value:
            universal_item["args"] = stats_func_addarg_value[f'{universal_item["func_name"]}|add_args'][0]
        else:
            universal_item["args"] = []
        
        # universal_kargs
        stats_func_karg_value.update(stats_func_arg_value)
        final_kargs = {}
        for karg_key, karg_values in stats_func_karg_value.items():
            if "|" in karg_key:
                karg_key = karg_key.split("|")[-1]
            if universal_version == 1:
                # Universal 1 - value is a list of tuple (value, default_value)
                final_kargs[karg_key] = karg_values
            elif universal_version == 2:
                # Universal 2 - value is a list of values
                final_kargs[karg_key] = [karg_value for karg_value, _ in karg_values]
            else:
                raise ValueError("Invalid universal version")
        universal_item["kargs"] = final_kargs
        
        # target_lib
        universal_item["target_lib"] = func_usage["target_lib"]
        return universal_item
    else:
        return None


if __name__ == "__main__":
    matplotlib_schema_dict = load_matplotlib_schema(matplotlib_schema_dir="./matplotlib_schema", 
                                                    version_list=["3.8.1", "2.2.5" ,"1.5.3"])
    verbose = False
    
    glob_path = "/Users/nngu0448/Documents/data/the-stack/Python/matplotlib_code/*.py.json"
    paths = sorted(glob.glob(glob_path))
    for path in tqdm(paths):
        uni_path = path.replace(".py.json", ".universal.jsonl")
        fo = open(uni_path, mode="w", encoding="utf-8")
        with open(path, mode="r", encoding="utf-8") as fi:
            for line in fi:
                if line.strip() != "":
                    func_usage = json.loads(line.strip())
                    universal_item = convert_to_universal_format(func_usage, matplotlib_schema_dict, verbose=verbose)
                    if universal_item:
                        fo.write(json.dumps(universal_item)+"\n")
                        if verbose:
                            print(json.dumps(universal_item))
                            print()
        fo.close()
    print("Done----------")
    
    error_dict = sorted(error_dict.items(), key=lambda x: x[1], reverse=True)
    for key, value in error_dict:
        print(key, value)


    
    
