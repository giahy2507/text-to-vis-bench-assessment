# Do Text-to-Vis Benchmarks Test Real Use of Visualizations?

## Downloading data

Data was downloaded from [the stack](https://huggingface.co/datasets/bigcode/the-stack-dedup) dataset for Python, R, Javascript, and JSON.
It requires a disk of around 300GB for storing all parts of a language.

```bash
# If it is cashed, resume with the same command
# Downloading via streamming "load_dataset(stream=True)" is not a good solution as the connections will brokens and crash the program.
# lang_dir you can find at "https://huggingface.co/datasets/bigcode/the-stack-dedup/tree/main/data"
python download_code_hg_face.py\
    --dataset_name "bigcode/the-stack-dedup"\
    --lang_dir "data/python"\
    --output_dir "../data/raw-data/the-stack/"\
    --hugging_face_token "XXXXXXXXXXXXXXXXXXXXXXXX"

# after download to a jsonl file, you can filter them targetting a specific library
python extract_code.py \
    --input_path "../data/raw-data/the-stack/Python.jsonl"\
    --output_path "../data/raw-data/the-stack/Python.matplotlib.jsonl"\
    --list_patterns "import matplotlib.pyplot as plt" "#PARTERN #2" "#PARTERN #3"
```

## Parsing and Converting Universal Format

### 1. Python-based Datasets
```bash
# Modify the input and output paths in the files below to run the parsing code for each dataset.

## Matplotlib_Python - Example
# - matplotlib_schema_dir: the path to the schema of the library (e.g., "${REPO_DIR}/data/raw-data/schema/matplotlib_schema")
# - jsonl_file_path: obtained from the above (e.g., "${REPO_DIR}/data/raw-data/the-stack/Python.matplotlib.jsonl")
# - output_file_path: the output jsonl for universal 2 data (e.g., "${REPO_DIR}/data/universal/Matplotlib_Python.universal2.jsonl")
python python_code/main_matplotlib_python.py

## Matplotlib_Notebook
python python_code/main_matplotlib_notebook.py

## PlotCoder
python python_code/main_plot_coder.py

## ChartDialog
python python_code/main_chartdialog.py
```

### 2. R - Graphics
This step requires to install [R (brew)](https://formulae.brew.sh/formula/r) and [R Studio](https://posit.co/download/rstudio-desktop/)

Open R studio with the folder `R_code`, and run the following command
```bash
Rscript main.R
```
Then use Python code to transform to universal format
```bash
# Modify the input and output paths in the file below to run the code.
python python_code/main_r_graphics.py
```

### 3. Vega-lite dataset
```bash
# Vega-lite
# Modify the input and output paths in the file below to run the code.
python python_code/main_vegalite.py
```

### 4. [nvBench](https://github.com/TsinghuaDatabaseGroup/nvBench)
```bash
# Vega-lite
# Modify the input and output paths in the file below to run the code.
python python_code/main_vegalite.py
```

### 5. JavaScript - ChartJS
This requires installing
- [Node.js](https://nodejs.org/en/download/)
- [npm](https://www.npmjs.com/get-npm)


Install the dependencies
```bash
cd preprocessing_data/JS_code
npm init
npm install
```

Converting data
```bash
# Extracting data to JSON files
# Input_path is from `Downloading data` section
python preprocessing_data/python_code/the_stack_to_files.py\
    --thestack_jsonl_path "../data/raw-data/the-stack/JavaScript.chartjs.jsonl"\
    --thestack_output_dir "../data/raw-data/the-stack/JavaScript_ChartJS"

# Parsing JS files to AST Tree using Javascript acorn-loose
# The output are files in JSON format
cd preprocessing_data/JS_code
node src/convert_to_ast.js

# Converting AST to Universal format
# cd back to the repository root
# Modify the input and output paths in the file below to run the code.
python preprocessing_data/python_code/main_js_chartjs.py


```
  




