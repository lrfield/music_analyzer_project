from vis_utils.pie_chart import plot_pie_chart
from vis_utils.image_conversion import convert_matplot_fig_to_image
from mongodb_queries.db_constants import db, artists_col, genres_col, listeners_col
import matplotlib as plt

# Pie chart of voted genre tag distribution for a given artist
def artist_genre_tag_pie_chart(name):
  tag_counts_wrapped = artists_col.find_one(
      {"name": name},
      {"_id":0, "name":1,"tag_counts":1}
  )
  if tag_counts_wrapped and tag_counts_wrapped.get("tag_counts"):
    tag_counts_list = tag_counts_wrapped.get("tag_counts", [])
    tag_names  = [tag_count["tag"]   for tag_count in tag_counts_list]
    tag_counts = [tag_count["count"] for tag_count in tag_counts_list]
    
    fig, ax = plot_pie_chart(tag_counts,tag_names)
    result = convert_matplot_fig_to_image(fig)
    plt.close(fig)
    return result
  else:
    print("No tags found")

# Pie chart of top countries for a genre
def genre_country_pie_chart(name):
  country_count_wrapped = genres_col.find_one(
      {"_id": name},
      {"_id":1, "top_countries":1}
  )
  if country_count_wrapped and country_count_wrapped.get("top_countries"):
    country_counts_dict = country_count_wrapped["top_countries"]
    countries = [entry["_id"] for entry in country_counts_dict]
    country_listen_counts = [entry["unique_listeners"] for entry in country_counts_dict]
    
    fig, ax = plot_pie_chart(country_listen_counts, countries)
    result = convert_matplot_fig_to_image(fig)
    plt.close(fig)
    return result
  else:
    print("No Countries found")

# Plot the distribution of the top 10 artists within a genre
def genre_artist_pie_chart(name):
  artist_count_wrapped = genres_col.find_one(
      {"_id": name},
      {"_id":1, "top_artists":1}
  )
  if artist_count_wrapped and artist_count_wrapped.get("top_artists"):
    artist_counts_dict = artist_count_wrapped["top_artists"]
    artists = [entry["name"] for entry in artist_counts_dict]
    artist_listen_counts = [entry["unique_listeners"] for entry in artist_counts_dict]
    fig, ax = plot_pie_chart(artist_listen_counts, artists)
    result = convert_matplot_fig_to_image(fig)
    plt.close(fig)
    return result 
  else:
    print("No Artists found")

# Plot the distribution of a listeners top artists
def listener_artist_pie_chart(name):
  artist_count_wrapped = listeners_col.find_one(
      {"_id": name},
      {"_id": 1, "listening_activity": 1}
  )

  if artist_count_wrapped and artist_count_wrapped.get("listening_activity"):
      activity = artist_count_wrapped["listening_activity"]
      artists = [entry["artist_name"] for entry in activity]
      artist_listen_counts = [entry["listen_count"] for entry in activity]
      fig, ax = plot_pie_chart(artist_listen_counts, artists)
      result = convert_matplot_fig_to_image(fig)
      plt.close(fig)
      return result
  else:
      print("No Artists found")
