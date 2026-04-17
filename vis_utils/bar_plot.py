import matplotlib.pyplot as plt
import pandas as pd

# code taken from https://towardsdatascience.com/7-steps-to-help-you-make-your-matplotlib-bar-charts-beautiful-f87419cb14cb/
def plot_bar(data, x_axis_title, y_axis_title, bar_color,
             figsize, bar_height, sort=True, title = None, 
             bar_color_map = None, col_to_det_color = None):
    # data should look like {'category': 'category', 'value': 'value'}
    df=pd.DataFrame(data)
    print(df[col_to_det_color])
    # color bars with dict (tag colors)
    if bar_color_map is not None:
        df["color"] = df[col_to_det_color].map(bar_color_map)
    
    
    # Sorting bars in ascending order
    if(sort):
        df = df.sort_values(by="value")   


    # Horizontal layout bar plotting statements
    fig, ax = plt.subplots(figsize=figsize)

    bars = ax.barh(
        df["category"],
        df["value"],
        height = bar_height,
        color=df["color"]
    )

    ax.margins(y=0) 

    # remove spines
    ax.spines[["right", "top"]].set_visible(False)


    # Add bar labels if there are explicitly defined ones in the dataframe, otherwise the bar labels 
    # will be the numerical values of the bar
    labels_present = "label" in df.columns
    bar_labels = df["label"].tolist() if labels_present else None

    # Add data labels
    bar_labels_graph = ax.bar_label(
        bars,
        labels = bar_labels,
        padding= 5,
        color="black",
        fontsize=12,
        label_type="edge",
        fmt="%.1f",
        fontweight="bold"
    )

    # setting tick label size
    ax.yaxis.set_tick_params(labelsize=14)


    # setting the font
    if y_axis_title:
        ax.set_ylabel(y_axis_title, fontsize=13, fontfamily = 'DejaVu Sans Mono')

    if x_axis_title:
        ax.set_xlabel(x_axis_title, fontsize=13, fontfamily = 'DejaVu Sans Mono')

    # graph title
    if title:
        ax.set_title(
            title,
            fontsize=16,
            fontweight="bold",
            pad=20,
            fontfamily = 'DejaVu Sans Mono'
        )

    # setting the font and color for elements that dont accept fontfamily as a parameter
    for i, label in enumerate(bar_labels_graph):
        label.set_fontfamily('DejaVu Sans Mono')
        label.set_color(df["color"].iloc[i])

    for label in ax.get_yticklabels():
        label.set_fontfamily('DejaVu Sans Mono')

    plt.tight_layout()
    return fig, ax