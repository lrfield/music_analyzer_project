# Sources code was replicated from:
# https://stackoverflow.com/questions/41416498/dendrogram-or-other-plot-from-distance-matrix
# https://www.learndatasci.com/glossary/hierarchical-clustering/
# https://jocelyn-ong.github.io/hierarchical-clustering-in-SciPy/


import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy import spatial
import matplotlib.pyplot as plt

def plot_dendrogram(df):

    # plot height has to be dependent on the number of elements or the text gets vertically crushed
    plot_height = int(len(df.columns)/5)

    figsize=(10, plot_height)
    fig, ax = plt.subplots(figsize=figsize)

    # Co-occurence matrices are not necessarily symmetric because of the summing
    # methods that we are using with genre tags, have to average the transpose to make it symmetric
    df_sym = (df + df.T) / 2
    # convert co-occurence to distance by inversion (if something occurs with something else 99 times, it should
    # be very close, so that turns into a small number, while something occuring only once concurrently
    # should become a large number)
    distance_grid = 1 / (df_sym + 1)
    # I was getting errors that the diagonal was not zero. I think this is a result of the +1
    # in the inversion step. Now I'm manually setting the diagonal to zero
    distance_array = distance_grid.values.copy()
    np.fill_diagonal(distance_array, 0)
    # From jocelyn.org tutorial
    y = spatial.distance.squareform(distance_array)
    # from learndatasci tutorial
    Z = linkage(y, method="ward", metric='euclidean')
    
    # dendogram doesn't have a font argument, setting beforehand
    
    # color threshold tuned from trial and error
    # this determines how far down the branches the color in the graph changes
    color_threshold = 0.3 * max(Z[:, 2])
    # combined info from learndatasci and stackoverflow for function call
    plot = dendrogram(Z, 
            labels=df.index.tolist(), 
            leaf_font_size = 10, 
            orientation="left", 
            color_threshold=color_threshold,
            ax=ax) 
    
    for lbl, color in zip(ax.get_ymajorticklabels(), plot['leaves_color_list']):
        lbl.set_color(color)

    plt.rcParams['font.family'] = 'DejaVu Sans Mono'
    return fig, ax