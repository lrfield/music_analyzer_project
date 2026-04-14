import io
import base64
import matplotlib
# Have to do this to prevent crashes from the matplotlib GUI opening
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Code taken from
# "How to use Matplotlib in a web application server" Section
# of matplotlib howto faq
# https://matplotlib.org/3.1.1/faq/howto_faq.html#how-to-use-matplotlib-in-a-web-application-server
def convert_matplot_fig_to_image(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)

    return image_base64