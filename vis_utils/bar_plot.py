import matplotlib.pyplot as plt
import pandas as pd

# code taken from https://towardsdatascience.com/7-steps-to-help-you-make-your-matplotlib-bar-charts-beautiful-f87419cb14cb/
def plot_bar(data, x_axis_title, y_axis_title, highlight_color, bar_color,
             figsize, bar_height, cutoff = None, sort=True, title = None):
    # data should look like {'category': 'category', 'value': 'value'}
    df=pd.DataFrame(data)

    # Cutoff
    if cutoff is not None:
        df["color"] = df["value"].apply(
            lambda x: highlight_color if x >= cutoff else bar_color
        )
    else: 
        df["color"] = bar_color
    
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

    # remove spines and x-axis
    ax.spines[["right", "top", "bottom"]].set_visible(False)
    ax.xaxis.set_visible(False)

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

    # making the cutoff line
    if cutoff is not None:
        ax.axvline(x=cutoff, zorder=0, color="grey", ls="--", lw=1.5)
        ax.text(
            x=cutoff,
            y=1,
            s=f"Cutoff: {cutoff}",
            ha="center",
            fontsize=13,
            fontfamily = 'DejaVu Sans Mono',
            bbox=dict(facecolor="white", edgecolor="grey", ls="--")
        )

    if y_axis_title:
        ax.set_ylabel(y_axis_title, fontsize=13, fontfamily = 'DejaVu Sans Mono')

    if title:
        ax.set_title(
            title,
            fontsize=16,
            fontweight="bold",
            pad=20,
            fontfamily = 'DejaVu Sans Mono'
        )

    # setting the font for elements that dont accept fontfamily as a parameter
    for label in bar_labels_graph:
        label.set_fontfamily('DejaVu Sans Mono')
    for label in ax.get_yticklabels():
        label.set_fontfamily('DejaVu Sans Mono')

    plt.tight_layout()
    return fig, ax