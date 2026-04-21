from flask import Flask, render_template
from vis_utils.artist_image import get_artist_image

from vis_utils.query_display_source import query_display_list
# list of arguments and functions used to display the drop down
# "MongoDB Query Used To Create Element" thing

import random

import page_elements.pie_chart_queries as pie_chart
import page_elements.bar_plot_queries as bar_plot
import page_elements.map_queries as map
import page_elements.dendrogram_queries as dendrogram

import mongodb_queries.listener_col_queries as listener_query
import mongodb_queries.artist_col_queries as artist_query
import mongodb_queries.genre_col_queries as genre_query

# Patterns for address based navigation, render template flask page organization
# taken from this resource:

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates

app = Flask(__name__)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Home tab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/')
def home():

    # ARTIST COL QUERIES
    # Data summary section
    total_num_artists = artist_query.get_total_num_artists()
    # List of artists section
    top_artists = artist_query.get_top_artists()

    # GENRE COL QUERIES
    # Data summary section
    total_num_genres = genre_query.get_total_num_genres()
    # Colors for tag hyperlinks in list of artists section
    tag_colors = genre_query.get_color_for_tags()

    # LISTENER COL QUERIES
    # Data summary section
    total_num_listeners = listener_query.get_total_num_listeners()

    # 
    # Data summary section
    percent_metal = round((artist_query.get_num_artists_in_genre("metal") / total_num_genres) * 100, 2)
    
    return render_template('index.html', 
                           query_display_list = query_display_list,
                           top_artists=top_artists, 
                           tag_colors = tag_colors,
                           total_num_artists = total_num_artists,
                           total_num_genres = total_num_genres,
                           total_num_listeners = total_num_listeners,
                           percent_metal = percent_metal
                           )

# Specified address for home tab that just shows all of the artists in the dataset
@app.route('/all_artists')
def all_artists():
    # ARTIST COL QUERIES
    # List of artists section
    all_artists = artist_query.get_all_artists()

    # GENRE COL QUERIES
    # Colors for tag hyperlinks in list of artists section
    tag_colors = genre_query.get_color_for_tags()
    return render_template('index.html', 
                           query_display_list = query_display_list,
                           all_artists=all_artists, 
                           tag_colors = tag_colors,
                           )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Report tab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/report')
def report():
    return render_template('report.html')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Artist tab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# no artist specified thru address
@app.route('/artist')
def artist():
    # VISUALIZATION ELEMENTS
    artist_map, artist_map_list = map.plot_artist_origin_by_country()
    artist_bar, artist_bar_list = bar_plot.plot_artists_origin_by_year()

    # GENRE COL QUERIES
    tag_colors = genre_query.get_color_for_tags()
    return render_template('artist.html', 
                           query_display_list = query_display_list,
                           artist_map=artist_map, 
                           artist_map_list = artist_map_list,
                           artist_bar=artist_bar,
                           artist_bar_list = artist_bar_list,
                           tag_colors = tag_colors)

# artist specified through address
@app.route('/artist/<path:name>')
def artist_detail(name):
    # ARTIST COL QUERIES
    # rank displayed top right main page
    artist_rank = artist_query.get_artist_rank_by_unique_listeners(name)
    # doc to draw several page elements from
    # used as jinja conditional for determining if page has a legit artist entry to display
    artist_doc = artist_query.get_artist(name)

    # LISTENER COL QUERIES
    # top listeners section near bottom
    artist_top_listeners = listener_query.get_listeners_of_artist(name, 20)
    # similar artists section at bottom
    artist_similar_artists = listener_query.get_similar_artists_simple(name, 20)

    # GENRE COL QUERIES
    # Colors for tag hyperlinks
    tag_colors = genre_query.get_color_for_tags()

    # VISUALIZATION ELEMENTS
    artist_pie_chart = pie_chart.artist_genre_tag_pie_chart(name)
    artist_image = get_artist_image(name) if artist_doc else None
    
    return render_template(
        'artist.html',
        query_display_list = query_display_list,
        artist_rank = artist_rank,
        artist_doc=artist_doc,
        artist_name=name,
        artist_top_listeners = artist_top_listeners,
        artist_similar_artists = artist_similar_artists,
        artist_pie_chart = artist_pie_chart,
        artist_image=artist_image,
        tag_colors = tag_colors
    )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Genre tab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# no genre specified thru address
@app.route('/genre')
def genre():
    # GENRE COL QUERIES
    # List of genres at bottom of page
    genre_list = genre_query.get_genres()
    # Colors for tag hyperlinks 
    tag_colors = genre_query.get_color_for_tags()

    # VISUALIZATION ELEMENTS
    genre_map, genre_map_list = map.plot_genre_origin_by_country()
    genre_bar, genre_bar_list = bar_plot.plot_genre_by_year()

    return render_template('genre.html', 
                           query_display_list = query_display_list,
                           genre_map=genre_map,
                           genre_map_list = genre_map_list,
                           genre_bar=genre_bar,
                           genre_bar_list = genre_bar_list,
                           genre_list = genre_list,
                           tag_colors = tag_colors)

# genre specified thru address
@app.route('/genre/<name>')
def genre_detail(name):
    # GENRE COL QUERIES
    # rank displayed top right main page
    genre_rank = genre_query.get_genre_rank_by_unique_listeners(name)
    # doc to draw several page elements from
    # used as jinja conditional for determining if page has a legit genre entry to display
    genre_doc = genre_query.get_genre(name)
    # Colors for tag hyperlinks and title
    tag_colors = genre_query.get_color_for_tags()

    # ARTIST COL QUERIES
    # list of artists in genre section
    artist_list = artist_query.top_artists_for_genre(name,100)
    # draw a random artist from the artist_list in the genre for the music player
    music_player_artist = random.choice(artist_list) if artist_list else None
    # similar genres to genre_name section
    similar_genres = artist_query.get_similar_genres_simple(name)

    # VISUALIZATION ELEMENTS
    # only preform if there is actually a doc for this genre
    if(genre_doc):
        artist_map, artist_map_list = map.plot_artist_origin_by_country(tag=name)
        genre_artist_pie_chart = pie_chart.genre_artist_pie_chart(name)
        genre_country_pie_chart = pie_chart.genre_country_pie_chart(name)
        artist_bar, artist_bar_list = bar_plot.plot_artists_origin_by_year(tag=name)
    else:
        artist_map, artist_map_list = None, None
        genre_artist_pie_chart = None
        genre_country_pie_chart = None, None
        artist_bar, artist_bar_list = None, None
    
    return render_template(
        'genre.html', 
        query_display_list = query_display_list,
        genre_rank = genre_rank,
        artist_map=artist_map, 
        artist_map_list = artist_map_list,
        artist_bar=artist_bar, 
        artist_bar_list = artist_bar_list,
        artist_list = artist_list,
        genre_name=name,
        genre_artist_pie_chart = genre_artist_pie_chart,
        genre_country_pie_chart = genre_country_pie_chart,
        genre_doc = genre_doc,
        music_player_artist = music_player_artist,
        tag_colors = tag_colors,
        similar_genres = similar_genres
        )

# preference display a dendrogram specified thru address
@app.route('/genre/dendrogram/<dendrogram_size>')
def genre_dendrogram(dendrogram_size):
    # convert string param to int
    dendrogram_size = int(dendrogram_size)
    # VISUALIZATION ELEMENTS
    # NOTE: if functioning correctly plot_genre_dendrogram should be drawing from
    # a cached image. Plotting dendrograms takes a long time and consumes RAM
    # If there are 502 errors it is likely due to this page not working right.
    genre_dendrogram = dendrogram.plot_genre_dendrogram(dendrogram_size)
    return render_template(
        'genre.html', 
        query_display_list = query_display_list,
        genre_dendrogram = genre_dendrogram,
        dendrogram_size = dendrogram_size
        )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Listener tab ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# no listener specified thru address
@app.route('/listener')
def listener():
    # LISTENER COL QUERIES
    top_listeners = listener_query.get_top_listeners()
    return render_template('listener.html',
                           query_display_list = query_display_list,
                           top_listeners = top_listeners)


# listener specified thru address
@app.route('/listener/<path:_id>')
def listener_detail(_id):
    # LISTENER COL QUERIES
    # rank displayed top right main page
    listener_rank = listener_query.get_listener_rank_by_play_count(_id)
    # doc used for several elements, used as jinja conditional to check if there is legit listener
    # entry to display
    listener_doc = listener_query.get_listener(_id)
    # total play count displayed right hand side
    listener_total_play_count = listener_query.get_total_play_count_for_listener(_id)

    # ARTIST COL QUERIES
    # hyperlinked pile of genre tags on the right hand side 
    listener_genres = artist_query.get_genres_for_listener(_id)
    # number of genres shown above pile of tags
    unique_genre_count = len(set(listener_genres)) if listener_genres else None

    # GENRE COL QUERIES
    # Colors for tag hyperlinks
    tag_colors = genre_query.get_color_for_tags()

    # VISUALIZATION ELEMENTS
    listener_artist_pie_chart = pie_chart.listener_artist_pie_chart(_id)
    
    return render_template(
        'listener.html', 
        query_display_list = query_display_list,
        listener_rank = listener_rank,
        listener_doc=listener_doc, 
        listener_name=_id,
        listener_artist_pie_chart = listener_artist_pie_chart,
        listener_genres = listener_genres,
        listener_total_play_count = listener_total_play_count,
        unique_genre_count = unique_genre_count,
        tag_colors = tag_colors)

if __name__ == '__main__':
    app.run(debug=False)