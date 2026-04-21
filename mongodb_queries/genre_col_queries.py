from mongodb_queries.db_constants import genres_col
import pymongo
import os

# This module contains the queries that access the genre_profile collection in the music
# database.

# IMPORTANT: The keys for the elements of returned dict elements from queries are essential
# For the hyperlinking html code to work. templates/list_table_macro.html generates links based on key names.

# Return a single genre document
def get_genre(_id):
    doc = genres_col.find_one({"_id": _id})
    return doc

# Return a dict where the keys are single genre names and the values are hex color strings
# This is for use in coloring genre text/plots
def get_color_for_tags():
    genres = genres_col.find({}, {"assigned_color": 1})
    color_map = {genre["_id"]: genre["assigned_color"] for genre in genres if "assigned_color" in genre}
    # handling case where artist has no specified genre
    color_map[None] = "#000000"
    return color_map

# Return the total number of unique genre tags in the collection
def get_total_num_genres():
    return genres_col.count_documents({})

# Return the position of a specific genre tag based on a sorted list of accumulated unique listeners
# Unique listeners is a bit of a misnomer here since they are double counted due to listeners listening to 
# multiple artists of the same genre, more accurately sum total listeners?
def get_genre_rank_by_unique_listeners(_id):
    genre = genres_col.find_one(
        {"_id": _id},
        {"total_unique_listeners": 1}
    )
    if not genre:
        return None

    genre_listener_count = genre["total_unique_listeners"]
    rank = genres_col.count_documents(
        {
            "total_unique_listeners": {
                "$gt": genre_listener_count
                }
        }
    ) 
    # address counting offset from gt
    rank += 1
    return rank

# Get a list of genre tag names sorted by total unique listeners
def get_genres(limit = 100):
    pipeline = [
        {
            "$match": {
                "total_unique_listeners": {
                    "$exists": True, "$ne": None
                    }
            }
        },
        {
            "$sort": {
                "total_unique_listeners": -1
                }
        },
        {
            "$limit": limit
        },
        {
            "$project": {
                "genre_name": "$_id", 
                "total_unique_listeners": 1
                }
        }
    ]
    genres = genres_col.aggregate(pipeline)
    return list(genres)

# Get the top genres for artists originating from a given country. This uses a shortcut
# by accessing the top 10 countries list in the genre doc instead of aggregating across all artists.
# I have found that it returns almost exactly the same result for a much less intensive query
# but it is technically not reflective of the dataset, since the countries corresponding to lower positions
# than 10 in a genres listening base are thrown away instead of aggregated.
def top_genres_in_country(country, limit=10):
    pipeline = [
        {
            "$unwind": "$top_countries"
        },
        {
            "$match":{
                "top_countries._id": country
            }
        },
        {
            "$sort":{
                "top_countries.unique_listeners":-1
            }
        },
        {
            "$limit": limit
        },
        {
            "$project": {
                "_id": 0,
                "genre": "$_id",
                "unique_listeners": "$top_countries.unique_listeners"
            }
        }
    ]

    top_genres = genres_col.aggregate(pipeline)
    return list(top_genres)