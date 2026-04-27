import pymongo
import os
from mongodb_queries.db_constants import artists_col
from mongodb_queries.listener_col_queries import get_artist_names_for_listener
# This module contains the queries that access the artist_profile collection in the music
# database.

# IMPORTANT: The keys for the elements of returned dict elements from queries are essential
# For the hyperlinking html code to work. templates/list_table_macro.html generates links based on key names.

# General overview: These templates are replicated across artist, listener, and genre collection queries
# I'm not going to put this boilerplate at the front of all of them but it applies to them too.

# ~~~~ Simple field retrieval functions ~~~~
# Basically just using find_one or count_documents

# ~~~~ Ranking Functions ~~~~
# return a number corresponding with the items place in a sorted list
# First, retrieve the doc, find the field to rank by, then count all docs
# with a higher value than sorted rank, and add one
# pattern for ranking functions taken from:

# https://groups.google.com/g/mongodb-user/c/EP8_-yUthq4?pli=1

# ~~~~ Getting a Sorted List of Items ~~~~
# All of these follow relatively the same pipeline based aggregation pattern,
# match -> sort -> limit -> project
# If you need to sort by a field that is within the nested objects
# match -> unwind -> match -> sort -> limit -> project

# These patterns were replicated from these tutorials:

# https://studio3t.com/knowledge-base/articles/mongodb-aggregation-framework/

# https://www.mongodb.com/docs/languages/python/pymongo-driver/current/aggregation/

# https://dev.to/arjun_computer_geek/mastering-mongodb-aggregation-4094


# get a single artist doc based on name
def get_artist(name):
    doc = artists_col.find_one({"name": name})
    return doc

# Get a list of all of the countries in the dataset based on the country field of all artist docs
def get_countries():
    countries = artists_col.distinct("country")
    # distinct() can return None if a document has no country field
    return sorted([c for c in countries if c])


def get_total_num_artists():
    return artists_col.count_documents({})


def get_num_artists_in_genre(genre):
    return artists_col.count_documents({"tag_counts.tag": genre})

# Return the position of a specific artist based on a sorted list of accumulated unique listeners

def get_artist_rank_by_unique_listeners(name):
    artist = artists_col.find_one(
        {"name": name},
        {"unique_listeners": 1}
    )

    if not artist:
        return None

    artist_listener_count = artist["unique_listeners"]
    rank = artists_col.count_documents(
        {
            "unique_listeners": {
                "$gt": artist_listener_count
                }
        }
    ) 
    # address counting offset
    rank += 1
    return rank

# Get a list of docs of the top artists in the dataset, sorted by unique listeners and limited by limit
def get_top_artists(limit=100):
    pipeline = [
        {
            "$sort": {
                "unique_listeners": -1
            }
        },
        {
            "$limit": limit
        },
        {
            "$project":{
                "_id": 0,
                "artist_name": "$name",
                "country": 1,
                "unique_listeners": 1,
                "genre_tags": "$tag_counts"
            }
        }
    ]

    artists = artists_col.aggregate(pipeline)
    return list(artists)

# same as get_top_artists but no limit, honestly this function is kind of redundant
def get_all_artists():
    pipeline = [
        {
            "$sort": {
                "unique_listeners": -1
            }
        },
        {
            "$project":{
                "_id": 0,
                "artist_name": "$name",
                "country": 1,
                "unique_listeners": 1,
                "genre_tags": "$tag_counts"
            }
        }
    ]

    artists = artists_col.aggregate(pipeline)
    return list(artists)

# Gewt the top artists within a genre by first using match to limit to artists who have a genre
# name inside of their tag_counts dict
def top_artists_for_genre(genre, limit=25):
    pipeline = [
        {
            "$match": {
                "tag_counts.tag":genre
                }
        },
        {
            "$sort": {
                "unique_listeners": -1
                }
        },
        {
            "$limit": limit
        },
        {
            "$project": {
            "_id": 0,
            "artist_name": "$name",
            "play_count": 1,
            "unique_listeners": 1,
            "country":1
        }
        }
    ]
    top_artists = artists_col.aggregate(pipeline)
    return list(top_artists)

# get the top artists who originated from a country, sorted by play_count
# NOTE: should probably change this to sorted by unique listeners for consistency
def top_artists_in_country(country, limit=10):
    pipeline = [
        {
            "$match": {
                "country": country
                }
        },
        {
            "$sort": {
            "play_count": -1
            }
        },
        {
            "$limit": limit
        },
        {
            "$project": {
                "name": 1
        }
        }
    ]
    top_artists = artists_col.aggregate(pipeline)
    return [doc["name"] for doc in top_artists]

# When provided with a listener, use get_artist_names to get a list of artists
# Then query that thru the artist collection to get a list of genre tags that those artists have
# It was difficult to decide which module to put this function in
def get_genres_for_listener(_id):
    artist_names = get_artist_names_for_listener(_id)
    if not artist_names:
        return None

    pipeline = [
        {
            "$match": {
                "name": {"$in": artist_names}
            }
        },
        {
            "$unwind": "$tag_counts"
        },
        {
            "$group": {
                "_id": "$tag_counts.tag"
            }
        },
        {
            "$project": {
                "_id": 0,
                "genre_name": "$_id"
            }
        }
    ]

    genres = artists_col.aggregate(pipeline)
    return [doc["genre_name"] for doc in genres]

# Get similar genres to the provided genre by querying the artist docs for co-occuring genre tags in artists
# Sister function to get_similar_artists, follows the same pattern.

def get_similar_genres_simple(genre_name, limit = 10):
    pipeline = [
        {
        # limit search set to artist documents that contain tag
            "$match": {
                "tag_counts.tag": genre_name
            }

        },
        # undwind tag_counts so that each element of the list can be treated as
        # its own object
        {
            "$unwind": "$tag_counts"
        },

        # Remove the input genre from the count 
        {
            "$match": {
                "tag_counts.tag":{"$ne":genre_name}
            }
        },
        # group by genres occurring in the same artist, take the sum of when this happens
        {
            "$group": {
                "_id": "$tag_counts.tag",
                "co-occurence_count": {"$sum": "$tag_counts.count"}
            }
        },
        # rank by the amount of times genres appear together
        {
            "$sort": {"co-occurence_count": -1}
        },
        # return top # of similar genres
        {
            "$limit": limit
        },
        # convert the grouped genres back into a single genre list
        {
            "$project": {
                "_id": 0,
                "genre_name": "$_id",
                "co-occurence_count": 1
            }
        }
    ]

    return list(artists_col.aggregate(pipeline))