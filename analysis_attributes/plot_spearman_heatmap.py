import pandas as pd
from scipy import stats

tsv_path = "data/result_analysis_attributes/summary_stats_percentage.tsv"

# read tsv file by pandas
df = pd.read_csv(tsv_path, sep='\t')

heat_map_values = []
# print column Matplotlib_Python
columns = ["Matplotlib_Notebook", "Matplotlib_Python", "Graphics_R", "ChartJS_JavaScript", "Vegalite_Vega", "PlotCoder_Matplotlib_Python", "ChartDialog_Matplotlib_Python", "nvBench_Vegalite_Vega"]
for i in range(len(columns)):
    values = []
    for j in range(0, len(columns)):
        x = df[columns[i]]
        y = df[columns[j]]
        res = stats.spearmanr(x/100, y/100)
        # print(columns[i], columns[j], res.correlation, res.pvalue)
        # print(res.pvalue, end='\t')
        values.append(res.correlation)
    # print()
    heat_map_values.append(values)


# draw a heat map for the correlation values
# not display the lower triangle
# scale of color from light yellow to blue
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

columns_ticks = ["Matplotlib-nb", "Matplotlib-py", "Graphics", "ChartJS", "Vega-Lite", "PlotCoder", "ChartDialog","nvBench"]

mask = np.zeros_like(heat_map_values, dtype=bool)
mask[np.tril_indices_from(mask)] = True

axes = sns.heatmap(heat_map_values, 
                   mask=mask, 
                   annot=True, 
                   xticklabels=columns_ticks, 
                   yticklabels=columns_ticks, 
                   cmap='YlGnBu')

# x-axis on top
axes.xaxis.tick_top()

# for xtick labels: "PlotCoder", "ChartDialog", "nvBench" --> red color
# for ytick labels: "Matplotlib", "Graphics", "ChartJS", "Vegalite" --> black color
for label in axes.get_xticklabels():
    if label.get_text() in ["PlotCoder", "ChartDialog", "nvBench"]:
        label.set_color('red')
    else:
        label.set_color('black')

for label in axes.get_yticklabels():
    if label.get_text() in ["PlotCoder", "ChartDialog", "nvBench"]:
        label.set_color('red')
    else:
        label.set_color('black')

# set bigger font size for xtick labels
for label in axes.get_xticklabels():
    label.set_fontsize(12)

# set bigger font size for ytick labels
for label in axes.get_yticklabels():
    label.set_fontsize(12)

# rorate xtick labels
plt.xticks(rotation=20)

# grid + brackground
plt.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray', alpha=0.2)
plt.tight_layout()
plt.show()

# save figure with 300 dpi
# plt.savefig('correlation_heatmap.png', dpi=300)


