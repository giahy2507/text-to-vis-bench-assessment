import os
import subprocess

def get_file_length(path):
    assert os.path.isfile(path)
    s = subprocess.check_output(f"wc -l {path}", shell = True)
    s = s.decode("utf-8").strip()
    length = s.split()[0]
    return int(length)

def write_code_file(path, code_content):
    with open(path, mode="w", encoding="utf-8") as fo:
        fo.write(code_content)

def flatten_json(json_data, parent_key='', sep='|'):
    items = []
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            if isinstance(value, (dict, list)):
                items.extend(flatten_json(value, new_key, sep=sep))
            else:
                items.append((new_key, value))
    elif isinstance(json_data, list):
        for index, item in enumerate(json_data):
            new_key = f"{parent_key}[{index}]"
            if isinstance(item, (dict, list)):
                items.extend(flatten_json(item, new_key, sep=sep))
            else:
                items.append((new_key, item))
    return items