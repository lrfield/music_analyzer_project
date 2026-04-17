from vis_utils.country_mapping import plot_world_map
from vis_utils.image_conversion import convert_matplot_fig_to_image, save_file_to_cache, read_file_from_cache
from db_constants import db, artists_col, genres_col, listeners_col


def plot_artist_origin_by_country(tag = None):
    # The filtering section/$match stage has to be constructed seperately
    # This is because I wanted to have the default call to the function graph
    # without filtering by genre tags.
    # There is no way to do that without appending the tag filter outside of the pipeliene (at least that I know of)

    # caching map for commonly repeated query: origin by country without tag
    if(tag == None):
        artist_country_map_file = read_file_from_cache('map_cache', "artist_country_map_no_tag")
        if(artist_country_map_file):
            print("Returning locally computed artist country map (no tags) stored in static")
            return artist_country_map_file

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
        }
    ]

    top_artists_by_country = list(artists_col.aggregate(pipeline))

    if not top_artists_by_country:
        return None

    data = [
        {'country': country['_id'], 'value': country['name'], 'color_value': country['unique_listeners']}
        for country in top_artists_by_country
    ]

    fig, ax = plot_world_map(data)
    artist_country_map_file = convert_matplot_fig_to_image(fig)
    # saving no tag case to cache
    
    if(tag == None):
        print("Saving result to cache in static")
        save_file_to_cache('map_cache', "artist_country_map_no_tag", artist_country_map_file)
    return artist_country_map_file


def plot_genre_origin_by_country():

    genre_country_map_file = read_file_from_cache('map_cache', "genre_country_map")
    if(genre_country_map_file):
        print("Returning locally computed genre country map stored in static")
        return genre_country_map_file

    pipeline = [
        {
            "$unwind": "$top_countries"
        },
        {
            "$project": {
                "genre":              "$_id",
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
                "genre": {"$first": "$genre"},
                "unique_listeners": {"$first": "$unique_listeners"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "country": "$_id",
                "genre": 1,
                "unique_listeners": 1
            }
        },
        {
            "$sort": {"country": 1}
        }
    ]

    top_genres_by_country = list(genres_col.aggregate(pipeline))

    data = [
        {'country': entry['country'], 'value': entry['genre'], 'color_value': entry['unique_listeners']}
        for entry in top_genres_by_country
    ]

    fig, ax = plot_world_map(data)
    genre_country_map_file = convert_matplot_fig_to_image(fig)
    # saving map to cache
    print("Saving result to cache in static")
    save_file_to_cache('map_cache', "genre_country_map", genre_country_map_file)
    return genre_country_map_file