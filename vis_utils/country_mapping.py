import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import pandas as pd
import geopandas as gpd

import os
import urllib.request

SHAPEFILE_URL   = "https://github.com/nvkelso/natural-earth-vector/raw/master/geojson/ne_110m_admin_0_countries.geojson"
SHAPEFILE_CACHE = os.path.join(os.path.dirname(__file__), "ne_110m_admin_0_countries.geojson")

def _get_world():
    if not os.path.exists(SHAPEFILE_CACHE):
        urllib.request.urlretrieve(SHAPEFILE_URL, SHAPEFILE_CACHE)
    return gpd.read_file(SHAPEFILE_CACHE)

def country_text_sizer(country_code):

    country_sizes = {
        "large": ["AO","AR","AU","BO","BR","CA","CD","CN","CO","DZ","EG","ET","GL","ID","IN","IR","KZ","LY","ML","MN","MR","MX","NE","PE","RU","SA","SD","TD","US","ZA"],
        "medium": ["AF","BF","BW","BY","CF","CG","CI","CL","CM","DE","EC","EH","ES","FI","FR","GA","GB","GH","GN","GY","IQ","IT","JP","KE","LA","MA","MG","MM","MZ","MY","NA","NG","NO","NZ","OM","PG","PH","PK","PL","PY","RO","SE","SO","SS","TH","TM","TR","TZ","UA","UG","UZ","VE","VN","YE","ZM","ZW"],
        "small": ["AE","AL","AM","AT","AZ","BA","BD","BE","BG","BI","BJ","BS","BT","BZ","CH","CR","CU","CZ","DJ","DK","DO","EE","ER","FJ","GE","GM","GQ","GR","GT","GW","HN","HR","HT","HU","IE","IL","IS","JM","JO","KG","KH","KP","KR","KW","LB","LK","LR","LS","LT","LV","MD","ME","MK","MW","NI","NL","NP","PA","PT","QA","RS","RW","SB","SI","SK","SL","SN","SR","SV","SY","SZ","TG","TJ","TL","TN","TW","UY","VU","XK"],
        "tiny": ["AD","AG","BB","BH","BN","CV","CY","DM","FM","GD","KI","KM","KN","LC","LI","LU","MC","MH","MT","MU","MV","NR","PS","PW","SC","SG","SM","ST","TO","TT","TV","VA","VC","WS"],
    }

    size_to_fontsize = {
        "large": 29,
        "medium": 12,
        "small": 5,
        "tiny": 4,
    }

    for size, codes in country_sizes.items():
        if country_code in codes:
            return size_to_fontsize[size]

    return 7

def plot_world_map(input_list, country_col='country', value_col='value', color_col='color_value'):

    # This function is based off of the code from this tutorial:
      # https://python-graph-gallery.com/web-map-europe-with-color-by-country/

    # convert data to a dataframe so it matches tutorial
    df = pd.DataFrame(input_list)

    world = _get_world()

    data = world.merge(df, how='inner', left_on='ISO_A2', right_on=country_col)

    # color mapping
    cmap = cm.YlOrRd

    min_val = data[color_col].min()
    max_val = data[color_col].max()
    norm = mcolors.Normalize(vmin=min_val, vmax=max_val)

    # plotting the background map
    fig, ax = plt.subplots(1, 1, figsize= (48,24))

    world.plot(ax=ax, color='white', edgecolor='black', linewidth=0.5)
    data.plot(ax=ax, column=color_col, cmap=cmap, norm=norm, edgecolor='white', linewidth=0.5)

    ax.set_xlim(-180, 180)
    ax.set_ylim(-60, 85)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # compute centroids for annotations
    data_projected = data.to_crs(epsg=3857)
    data_projected['centroid'] = data_projected.geometry.centroid
    data['centroid'] = data_projected['centroid'].to_crs(data.crs)

    # centroid adjustments for inaccurate map values
    adjustments = {
        'US': (10, -10),
        'CA': (-6, -7),
    }
    # annotate countries
    for index, item in data.iterrows():
        x, y = item['centroid'].coords[0]
        dx, dy = adjustments.get(item[country_col], (0, 0))
        x += dx
        y += dy
        ax.annotate(
            f"{item[country_col]}\n{item[value_col]}",
            (x, y),
            ha='center',
            fontsize=country_text_sizer(item[country_col]),
            fontfamily='DejaVu Sans Mono',
            color='green'
        )


    plt.tight_layout()

    return fig, ax