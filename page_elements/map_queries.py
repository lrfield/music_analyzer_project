from vis_utils.country_mapping import plot_world_map
from vis_utils.image_conversion import convert_matplot_fig_to_image
from vis_utils.cache import save_file_to_cache, read_file_from_cache, save_json_to_cache, read_json_from_cache
from mongodb_queries.db_constants import db, artists_col, genres_col, listeners_col
import pycountry

# convert ISO code to country name 
# https://pypi.org/project/pycountry/
def return_country_name(ISO_code):
    country = pycountry.countries.get(alpha_2=ISO_code)
    return country.name if country else None

def plot_artist_origin_by_country(tag = None):
    # The filtering section/$match stage has to be constructed seperately
    # This is because I wanted to have the default call to the function graph
    # without filtering by genre tags.
    # There is no way to do that without appending the tag filter outside of the pipeliene (at least that I know of)

    # caching map for commonly repeated query: origin by country without tag
    if(tag == None):
        artist_country_map_file = read_file_from_cache('map_cache', "artist_country_map_no_tag")
        top_artists_by_country  = read_json_from_cache('map_cache', "artist_country_map_no_tag_list")
        if((artist_country_map_file != None) and (top_artists_by_country != None)):
            print("Returning locally computed artist country map (no tags) stored in static")
            return artist_country_map_file, top_artists_by_country

    filter_section = {
        "country": {"$exists": True, "$ne": None}
    }

    if tag is not None:
        filter_section["tag_counts.tag"] = tag
    

    pipeline = [
        # Remove artists with no country from the pipeline
        {
            "$match": filter_section
        },

        # Sort artists by listener count descending
        {
            "$sort": {"unique_listeners": -1}
        },

        # Group artists by country, collapse by only including the first occurence in the listener count sorted list
        {
            "$group": {
                "_id": "$country",
                "name":{"$first":"$name"},
                "unique_listeners":{"$first":"$unique_listeners"}
            }
        },

        # sort the results alphabetically
        {
            "$sort": {"_id": 1}
        },
        # rename fields
        {
            "$project":{
                "country": "$_id",
                "artist_name":"$name",
                "unique_listeners": 1
            }
        }
    ]

    top_artists_by_country = list(artists_col.aggregate(pipeline))

    if not top_artists_by_country:
        return None

    data = [
        {'country': country['country'], 'value': country['artist_name'], 'color_value': country['unique_listeners']}
        for country in top_artists_by_country
    ]

    fig, ax = plot_world_map(data)
    artist_country_map_file = convert_matplot_fig_to_image(fig)

    # converting country ISO code to string country name in list
    # # important! this step should not take place before calling plot_world_map
    # # The map plotting needs ISO country codes 
    for artist in top_artists_by_country:
        country_string = return_country_name(artist['country'])
        if(country_string):
            artist['country'] = country_string

    # saving no tag case to cache
    if(tag == None):
        print("Saving result to cache in static")
        save_file_to_cache('map_cache', "artist_country_map_no_tag", artist_country_map_file)
        save_json_to_cache('map_cache', "artist_country_map_no_tag_list", top_artists_by_country)
    return artist_country_map_file, top_artists_by_country


def plot_genre_origin_by_country():

    genre_country_map_file = read_file_from_cache('map_cache', "genre_country_map")
    top_genres_by_country  = read_json_from_cache('map_cache', "genre_country_map_list")

    if((genre_country_map_file != None) and (top_genres_by_country != None)):
        print("Returning locally computed genre country map stored in static")
        return genre_country_map_file, top_genres_by_country

    pipeline = [
        {
            "$unwind": "$top_countries"
        },
        {
            "$project": {
                "genre_name":              "$_id",
                "country":            "$top_countries._id",
                "unique_listeners": "$top_countries.unique_listeners",
                "_id": 0
            }
        },
        {
            "$sort": {"unique_listeners": -1}
        },
        {
            "$group": {
                "_id": "$country",
                "genre_name": {"$first": "$genre_name"},
                "unique_listeners": {"$first": "$unique_listeners"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "country": "$_id",
                "genre_name": 1,
                "unique_listeners": 1
            }
        },
        {
            "$sort": {"country": 1}
        }
    ]

    top_genres_by_country = list(genres_col.aggregate(pipeline))

    data = [
        {'country': entry['country'], 'value': entry['genre_name'], 'color_value': entry['unique_listeners']}
        for entry in top_genres_by_country
    ]

    fig, ax = plot_world_map(data)
    genre_country_map_file = convert_matplot_fig_to_image(fig)

    # converting country ISO code to string country name in list
    # # important! this step should not take place before calling plot_world_map
    # # The map plotting needs ISO country codes 
    for genre in top_genres_by_country:
        country_string = return_country_name(genre['country'])
        if(country_string):
            genre['country'] = country_string


    # saving map to cache
    print("Saving result to cache in static")
    save_file_to_cache('map_cache', "genre_country_map", genre_country_map_file)
    save_json_to_cache('map_cache', "genre_country_map_list", top_genres_by_country)

    return genre_country_map_file, top_genres_by_country