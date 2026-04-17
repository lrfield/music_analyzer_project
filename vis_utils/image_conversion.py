import io
import base64
import matplotlib
# Have to do this to prevent crashes from the matplotlib GUI opening
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, hashlib

# Code taken from
# "How to use Matplotlib in a web application server" Section
# of matplotlib howto faq
# https://matplotlib.org/3.1.1/faq/howto_faq.html#how-to-use-matplotlib-in-a-web-application-server
def convert_matplot_fig_to_image(fig):
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png',bbox_inches='tight',pad_inches=0.2)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()
    plt.close(fig)
    return image_base64


# I found that caching some graphs (especially dendrograms) was very necessary
# they use enough memory to crash the website
# not caching by instance, I'm computing locally, storing in the static folder,
# then updating manually via github release.

# copying this code to create cache functions https://shawnway210.hashnode.dev/caching-in-python

def save_file_to_cache(cache_folder, cache_filename, file):
    CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', cache_folder)
    cache_path = os.path.join(CACHE_DIR, f"{cache_filename}.b64")
    os.makedirs(CACHE_DIR, exist_ok=True)  # creates the directory if it doesn't exist
    with open(cache_path, "w") as f:
        f.write(file)

def read_file_from_cache(cache_folder, cache_filename):
    CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', cache_folder)
    cache_path = os.path.join(CACHE_DIR, f"{cache_filename}.b64")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return f.read()
    else:
        return False