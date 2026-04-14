import matplotlib.pyplot as plt

# Function based off of this tutorial
# https://www.pythoncharts.com/matplotlib/pie-chart-matplotlib/

def autopct_filter(pct):
        return f'{pct:.1f}%' if pct >= 5 else ''

def plot_pie_chart(values, labels, title = None, figsize = (8,8)):
  
  fig, ax = plt.subplots(figsize=figsize)
  patches, texts, pcts = ax.pie(
    values, labels=labels, autopct=autopct_filter,
    wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'},
    textprops={'size': 'x-large'},
    startangle=90)
  
  
  # For each wedge, set the corresponding text label color to the wedge's
  # face color.
  for i, patch in enumerate(patches):
    texts[i].set_color(patch.get_facecolor())
    # Calculate the midpoint angle of the wedge
    angle = (patch.theta1 + patch.theta2) / 2
    # Flip labels on the left side so they don't render upside-down
    if 90 < angle < 270:
        angle += 180
    texts[i].set_rotation(angle)
    texts[i].set_rotation_mode('anchor')

  # Annoying necessity not included in tutorial:
  # Pie chart function does not include a font parameter
  # similarly to the wedge text color loop we have to set the 
  # font for all of the text on the graph

  for text in texts + list(pcts):
        text.set_fontfamily('DejaVu Sans Mono')
  plt.setp(pcts, color='white')
  plt.setp(texts, fontweight=600)
  if title:
    ax.set_title(title, fontsize=18, fontfamily = 'DejaVu Sans Mono')

  

  plt.tight_layout()

  return fig,ax
