# Do Text-to-Vis Benchmarks Test Real Use of Visualisations?
This repository includes the data, analysis code, and cross-language mappings discussed in the paper.

Our findings reveal a substantial gap in current Text-to-Vis datasets, with evaluations not testing the same distribution of chart types, attributes, and the number of actions. 
The only representative dataset requires modification to become an end-to-end and practical benchmark. 
This shows that new, more benchmarks are needed to support the development of systems that truly address users' visualisation needs. 
These observations will guide future data creation, highlighting which features hold genuine significance for users.


## Data
You can download the whole data in the release section and save it at `${REPO_DIR}/data` for the analysis.
It contains the processed datasets in universal format, located in the `data/universal` folder.
```bash
[
    {
        "file_id": "0",
        "content": [
            {
                "func_name": "plot", 
                "args": ["<class 'ast.Name'>"], 
                "kargs": {"color": ["black"], "linewidth": [10]}
            },
            ...
        ]
    },
    ...
]
```
Mappings are also available in the `data/mapping` and `data/mapping_when_permitted` folders.

## Analysis
Analysis section is divided into several sub-sections, each of which is a specific analysis in the paper.

#### Plot types
```bash
# Input data: "data/universal"
# Output data: in the console
python analysis_plottype/counting_plottype_python.py
python analysis_plottype/counting_plottype_R.py
python analysis_plottype/counting_plottype_chartjs.py
python analysis_plottype/counting_plottype_vegalite.py
```
After running the code and gathering countings in the console, we can obtain a [Sheet](https://docs.google.com/spreadsheets/d/1CcEblrSUnKP4FPWhSQZ3mLIVJbSAXP9VQFW-d4VTIyU/edit?usp=sharing), which contains the counting of plot types in each dataset.

#### Attributes
```bash
# Input data: "data/universal"
# Output data: 
#       - "data/counting"
#       - "data/result_analysis_attributes"
python analysis_attributes/counting_func_args.py
python analysis_attributes/counting_attributes.py


# plot Spearman's rank correlation coefficient
# Input data: "data/result_analysis_attributes"
# Output data: shown by Matplotlib
python analysis_attributes/plot_spearman_heatmap.py
```
#### Attributes when permitted
```bash
# Input data: 
#       - "data/mapping_when_permitted"
#       - "data/counting"
#       - "data/universal"
# Output data: 
#       - "data/result_analysis_attributes_when_permitted"
python analysis_attributes_when_permitted/counting_attributes_permitted.py
```

#### Complexity
```bash
# Input data: "data/universal"
# Output data: in the console
python analysis_complexity/counting_complexity.py
```

#### Values Used for Attributes (new finding, not in the paper)
I presented this analysis in this [Google Sheet](https://docs.google.com/spreadsheets/d/1dduAB5f9UiKpQ4esiVHkdmPNi63LfeY7Pbq2KzirbsM/edit?usp=sharing).
This analysis supports our conclusion that the distribution of values used in ChartDialogs is significantly misaligned with the distribution of real-world data. For instance, ChartDialogs includes `linewidth` values of `1.2`, `3`, and `5`, which are rarely used, while it omits commonly used values such as `1` and `2`.

## Cite
```
{

}
```

## Contact
- Ngoc Gia Hy Nguyen: nngu0448@uni.sydney.edu.au
- Dr. Jonathan K. Kummerfeld: jonathan.kummerfeld@sydney.edu.au

## Acknowledgments
This material is based in part on work supported by the Australian Research Council through a Discovery Early Career Researcher Award and by the Commonwealth Scientific and Industrial Research Organisation (CSIRO).