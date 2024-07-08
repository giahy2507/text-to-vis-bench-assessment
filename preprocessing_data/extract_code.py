import json
from pprint import pprint
from tqdm import tqdm
import re
import os
import subprocess
import argparse

def get_file_length(path):
    assert os.path.isfile(path)
    s = subprocess.check_output(f"wc -l {path}", shell = True)
    s = s.decode("utf-8").strip()
    length = s.split()[0]
    return int(length)


def extract_python_matplotlib(input_path, output_path):
    length = get_file_length(input_path)
    with open(output_path, mode="w", encoding="utf-8") as fo:
        with open(input_path, mode="r", encoding="utf-8") as fi:
            for line in tqdm(fi, total=length):
                data = json.loads(line)
                if "import matplotlib.pyplot as plt" in data["code"] and re.search("plt\.[0-9a-zA-Z]+", data["content"]):
                    fo.write(line)

def extract_code_with_pattern(input_path, output_path, pattens_str):
    # length = get_file_length(input_path)
    with open(output_path, mode="w", encoding="utf-8") as fo:
        with open(input_path, mode="r", encoding="utf-8") as fi:
            for line in tqdm(fi):
                data = json.loads(line)
                for patten_str in pattens_str:
                    if patten_str in data["content"]:
                        fo.write(line)
                        break


def main_extract_code_1():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str)  
    parser.add_argument('--output_path', type=str)
    parser.add_argument('--pattern_str', type=str)
    args = parser.parse_known_args()[0]

    extract_code_with_pattern(args.input_path,
                              args.output_path, 
                              pattens_str=[args.pattern_str])
    
    
def main_extract_code_2():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str)
    parser.add_argument('--output_path', type=str)
    parser.add_argument('--list_patterns', nargs='+', help='<Required> Set flag', required=True)
    args = parser.parse_known_args()[0]
    extract_code_with_pattern(args.input_path,
                              args.output_path, 
                              pattens_str=args.list_patterns)

if __name__ == "__main__":
    
    main_extract_code_2()
    

    
                    