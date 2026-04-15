from flask import Flask, render_template
from vis_utils.artist_image import get_artist_image
from vis_utils.query_display_source import query_display_list

import page_elements.pie_chart_queries as pie_chart
import page_elements.bar_plot_queries as bar_plot
import page_elements.map_queries as map
import page_elements.dendrogram_queries as dendrogram
import random
import db as database

# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-ii-templates

app = Flask(__name__)

@app.route('/')
def home():
    total_num_artists = database.get_total_num_artists()
    total_num_genres = database.get_total_num_genres()
    total_num_listeners = database.get_total_num_listeners()
    percent_metal = round((database.get_num_artists_in_genre("metal") / total_num_genres) * 100, 2)
    tag_colors = database.get_color_for_tags()
    top_artists = database.get_top_artists()
    return render_template('index.html', 
                           query_display_list = query_display_list,
                           top_artists=top_artists, 
                           tag_colors = tag_colors,
                           total_num_artists = total_num_artists,
                           total_num_genres = total_num_genres,
                           total_num_listeners = total_num_listeners,
                           percent_metal = percent_metal
                           )

@app.route('/all_artists')
def all_artists():
    all_artists = database.get_all_artists()
    tag_colors = database.get_color_for_tags()
    return render_template('index.html', 
                           query_display_list = query_display_list,
                           all_artists=all_artists, 
                           tag_colors = tag_colors,
                           )

@app.route('/report')
def report():
    return render_template('report.html')

@app.route('/artist')
def artist():
    
    artist_map = map.plot_artist_origin_by_country()
    artist_bar = bar_plot.plot_artists_origin_by_year()
    return render_template('artist.html', 
                           query_display_list = query_display_list,
                           artist_map=artist_map, artist_bar=artist_bar)

@app.route('/artist/<path:name>')
def artist_detail(name):
    artist_rank = database.get_artist_rank_by_unique_listeners(name)
    artist_doc = database.get_artist(name)
    artist_top_listeners = database.get_listeners_of_artist(name, 20)
    artist_similar_artists = database.get_similar_artists_simple(name, 20)
    artist_pie_chart = pie_chart.artist_genre_tag_pie_chart(name)
    artist_image = get_artist_image(name) if artist_doc else None
    tag_colors = database.get_color_for_tags()
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

@app.route('/genre')
def genre():
    genre_map = map.plot_genre_origin_by_country()
    genre_bar = bar_plot.plot_genre_by_year()
    genre_list = database.get_genres()
    tag_colors = database.get_color_for_tags()
    return render_template('genre.html', 
                           query_display_list = query_display_list,
                           genre_map=genre_map,
                           genre_bar=genre_bar,
                           genre_list = genre_list,
                           tag_colors = tag_colors)

@app.route('/genre/<name>')
def genre_detail(name):
    genre_rank = database.get_genre_rank_by_unique_listeners(name)
    genre_doc = database.get_genre(name)
    artist_map = map.plot_artist_origin_by_country(tag=name)
    genre_artist_pie_chart = pie_chart.genre_artist_pie_chart(name)
    genre_country_pie_chart = pie_chart.genre_country_pie_chart(name)
    artist_bar = bar_plot.plot_artists_origin_by_year(tag=name)
    artist_list = database.top_artists_for_genre(name,100)
    music_player_artist = random.choice(artist_list) if artist_list else None
    tag_colors = database.get_color_for_tags()
    similar_genres = database.get_similar_genres_simple(name)
    return render_template(
        'genre.html', 
        query_display_list = query_display_list,
        genre_rank = genre_rank,
        artist_map=artist_map, 
        artist_bar=artist_bar, 
        artist_list = artist_list,
        genre_name=name,
        genre_artist_pie_chart = genre_artist_pie_chart,
        genre_country_pie_chart = genre_country_pie_chart,
        genre_doc = genre_doc,
        music_player_artist = music_player_artist,
        tag_colors = tag_colors,
        similar_genres = similar_genres
        )

@app.route('/genre/dendrogram/<dendrogram_size>')
def genre_dendrogram(dendrogram_size):
    dendrogram_size = int(dendrogram_size)
    genre_dendrogram = dendrogram.plot_genre_dendrogram(dendrogram_size)
    return render_template(
        'genre.html', 
        query_display_list = query_display_list,
        genre_dendrogram = genre_dendrogram,
        dendrogram_size = dendrogram_size
        )

@app.route('/listener')
def listener():
    top_listeners = database.get_top_listeners()
    return render_template('listener.html',
                           query_display_list = query_display_list,
                           top_listeners = top_listeners)

@app.route('/listener/<path:_id>')
def listener_detail(_id):
    listener_rank = database.get_listener_rank_by_play_count(_id)
    listener_doc = database.get_listener(_id)
    listener_genres = database.get_genres_for_listener(_id)
    unique_genre_count = len(set(listener_genres)) if listener_genres else None
    listener_total_play_count = database.get_total_play_count_for_listener(_id)
    listener_artist_pie_chart = pie_chart.listener_artist_pie_chart(_id)
    tag_colors = database.get_color_for_tags()

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