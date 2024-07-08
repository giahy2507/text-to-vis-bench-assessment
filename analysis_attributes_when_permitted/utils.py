import os
import subprocess
import csv


def load_tsv_file(tsv_path, topk=None, return_dict=False):
    """
    Load a TSV file
    """
    with open(tsv_path, "r", encoding="utf-8") as fi:
        reader = csv.reader(fi, delimiter="\t")
        data = []
        for row in reader:
            data.append(row)
    if topk:
        data = data[: min(topk, len(data))]
    if return_dict:
        data = {row[0]: row[1] for row in data[1:]}
    return data

def get_file_length(path):
    """
    Count the number of lines in a file
    """
    assert os.path.isfile(path)
    s = subprocess.check_output(f"wc -l {path}", shell = True)
    s = s.decode("utf-8").strip()
    length = s.split()[0]
    return int(length)