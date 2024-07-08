"""
Condition guideline
-------------------

Each condition (tuple) contains 2 parts
1) First part: condition for non-keyword arguments (args)
- None: no condition
- list(): the considered value must be in the list
- ["!NOT"] + list() means the considered value must not be in the list
- "<class>": the considered value can be a variable name (the parser cannot extract the value)

2) Second part: condition for keyword arguments (kargs)
- {}: no condition
- {"key_name": "Any"}: the value of key_name can be any value
- {"key_name": None}: the key_name must not be in kargs of the calling function

"Any" means any values are accepted
"""

marker_list = [".", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h", "H", "+", "x", "X", "D", "d", "|", "_"]
line_style_list = ['-', '--', '-.', ':']
color_list = ["b", "g", "r", "c", "m", "y", "k", "w"]
"""
These list can be found in the matplotlib documentation
https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html
"""

all_list_conditions_2nd_version = {
    "# no condition": [],
    "# plot() exeption: with line attribute but no line width or style": [
        (None, {"linewidth": "0"}),
        (None, {"linewidth": "0.0"}),
        (None, {"LineWidth": "0"}),
        (None, {"LineWidth": "0.0"}),
        (None, {"lineWidth": "0"}),
        (None, {"lineWidth": "0.0"}),
        (None, {"Linewidth": "0"}),
        (None, {"Linewidth": "0.0"}),
        (None, {"lw": "0"}),
        (None, {"lw": "0.0"}),
        (None, {"linestyle": ""}),
        (None, {"linestyle": "None"}),
        (None, {"ls": ""}),
        (None, {"ls": "None"}),
    ],
    "# plot() markers": [
            (["<class>", ["!NOT"] + line_style_list ], {"linestyle": None, "ls": None}),
            (["<class>", "<class>", ["!NOT"] + line_style_list], {"linestyle": None, "ls": None}),
    ],
    "# heatmap": [
        (None, {"cmap": "Any"}),
        (None, {"vmin": "Any"}),
        (None, {"vmax": "Any"}),
    ]
}

plot_func_conditions_dict = {
    "plot": ["# no condition", "# plot() exeption: with line attribute but no line width or style", "# plot() markers"],
    "scatter": ["# no condition"],
    "bar": ["# no condition"],
    "barh": ["# no condition"],
    "hist": ["# no condition"],
    "pie": ["# no condition"],
    "imshow": ["# no condition", "# heatmap"],
    "contour": ["# no condition"],
    "contourf": ["# no condition"],
    "streamplot": ["# no condition"],
}
