import os
import json
from tqdm import tqdm
from utils_notebook import parse_ast_for_notebook_cells, filter_by_lines
from matplotlib_schema_parsing import load_matplotlib_schema


if __name__ == "__main__":
    # Load matplotlib schema - already prepared in "data/raw-data/schema/matplotlib_schema"
    # You can obtain the schema by running "python ./matplotlib_schema_parsing.py"
    matplotlib_schema_dir = "data/raw-data/schema/matplotlib_schema"
    matplotlib_schema_dict = load_matplotlib_schema(matplotlib_schema_dir=matplotlib_schema_dir, 
                                                    version_list=["3.8.1", "2.2.5" ,"1.5.3"])

    output_file_path = "data/universal/PlotCoder_Matplotlib_Python.universal2.jsonl"
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    # Follow https://github.com/jungyhuk/plotcoder
    # To download and process the juice dataset
    juice_dir = "data/raw-data/juice"
    input_files_name = ["dev_plot.json", 
                        "dev_plot_hard.json",
                        "test_plot.json", 
                        "test_plot_hard.json", 
                        "train_plot.json"]

    fo = open(output_file_path, mode="w", encoding="utf-8")

    for input_file_name in input_files_name:
        input_file_path = f"{juice_dir}/{input_file_name}"
        print(input_file_path)
        assert os.path.exists(input_file_path), f"{input_file_path} does not exist"

        json_data = json.load(open(input_file_path, mode="r", encoding="utf-8"))
        for i, item in tqdm(enumerate(json_data)):
            try:
                # extraction code from context + target code
                code_cells = []
                for j in range(len(item["context"])-1, -1, -1):
                    context = item["context"][j]
                    if context["cell_type"] == "code":
                        code_cells.append(filter_by_lines(context["code"]))
                code_cells.append(filter_by_lines(item["code"]))

                universal_items = parse_ast_for_notebook_cells(matplotlib_schema_dict, code_cells)
                if len(universal_items) > 0:
                    file_id = f"{input_file_name}_{i}"
                    fo.write(json.dumps({
                        "file_id": file_id,
                        "content": universal_items
                    }, ensure_ascii=False) + "\n")

            except Exception as e:
                # print(e)
                continue

    fo.close()


            