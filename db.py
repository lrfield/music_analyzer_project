import pymongo
import os
from db_constants import db, artists_col, genres_col, listeners_col

# ||||||||||||||| DATABASE MODULE |||||||||||||||

# This file contains the code for querying the MongoDB database to populate page information
# Queries related to visualization are in their own seperate files

# ~~~~ Simple field retrieval functions ~~~~

def get_artist(name):
    doc = artists_col.find_one({"name": name})
    return doc

def get_listener(_id):
    doc = listeners_col.find_one({"_id": _id})
    return doc

def get_genre(_id):
    doc = genres_col.find_one({"_id": _id})
    return doc

def get_countries():
    countries = artists_col.distinct("country")
    # distinct() can return None if a document has no country field
    return sorted([c for c in countries if c])

def get_color_for_tags():
    genres = genres_col.find({}, {"assigned_color": 1})
    return {doc["_id"]: doc["assigned_color"] for doc in genres if "assigned_color" in doc}

def get_total_num_artists():
    return artists_col.count_documents({})

def get_total_num_listeners():
    return listeners_col.count_documents({})

def get_total_num_genres():
    return genres_col.count_documents({})

def get_num_artists_in_genre(genre):
    return db.artists.count_documents({"tag_counts.tag": genre})

def get_total_play_count_for_listener(_id):
    doc = listeners_col.find_one(
        {"_id": _id},
        {"total_play_count": 1, "_id": 0}
    )
    if not doc:
        return None
    return doc["total_play_count"]

def get_artist_names_for_listener(_id):
    doc = listeners_col.find_one(
        {"_id": _id},
        {"listening_activity.artist_name": 1, "_id": 0}
    )
    if not doc:
        return None
    return [entry["artist_name"] for entry in doc["listening_activity"]]

# ~~~~ Ranking Functions ~~~~
# return a number corresponding with the items place in a sorted list
# First, retrieve the doc, find the field to rank by, then count all docs
# with a higher value than sorted rank, and add one

# pattern taken from https://groups.google.com/g/mongodb-user/c/EP8_-yUthq4?pli=1

def get_listener_rank_by_play_count(_id):
    listener = listeners_col.find_one(
        {"_id": _id},
        {"total_play_count": 1}
    )
    if not listener:
        return None

    listener_play_count = listener["total_play_count"]
    rank = listeners_col.count_documents(
        {
            "total_play_count": {
                "$gt": listener_play_count
                }
        }
    ) 
    # address counting offset
    rank += 1
    return rank

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
    # address counting offset
    rank += 1
    return rank

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

# ~~~~ Getting a Sorted List of Items ~~~~
# All of these follow relatively the same pipeline based aggregation pattern,
# match -> sort -> limit -> project
# If you need to sort by a field that is within the nested objects
# match -> unwind -> match -> sort -> limit -> project

# These patterns were replicated from these tutorials

# https://studio3t.com/knowledge-base/articles/mongodb-aggregation-framework/

# https://www.mongodb.com/docs/languages/python/pymongo-driver/current/aggregation/

# https://dev.to/arjun_computer_geek/mastering-mongodb-aggregation-4094

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
                "name": 1,
                "country": 1,
                "unique_listeners": 1,
                "tag_counts.tag": 1
            }
        }
    ]

    artists = artists_col.aggregate(pipeline)
    return list(artists)

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
            "name": 1,
            "play_count": 1,
            "unique_listeners": 1,
            "country":1
        }
        }
    ]
    top_artists = artists_col.aggregate(pipeline)
    return list(top_artists)


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

def get_top_listeners(limit=100):
    pipeline = [
        {
            "$sort": {
                "total_play_count": -1
            }
        },
        {
            "$limit": limit
        },
        {
            "$project": {
                "_id": 1,
                "total_play_count": 1
            }
        }
    ]

    listeners = listeners_col.aggregate(pipeline)
    return list(listeners)

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
                "_id": 1, "total_unique_listeners": 1
                }
        }
    ]
    genres = genres_col.aggregate(pipeline)
    return list(genres)


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


def get_listeners_of_artist(artist_name, limit =10):
    pipeline = [
        {
            "$match": {
                "listening_activity.artist_name": artist_name
            }
        },
        {
            "$unwind": "$listening_activity"
        },
        {
            "$match":{
                "listening_activity.artist_name": artist_name
            }
        },
        {
            "$project":{
                "_id": 1,
                "artist_listen_count": "$listening_activity.listen_count",
                "artist_name": "$listening_activity.artist_name"
            }
        },
        {
            "$sort": {"artist_listen_count":-1}
        },
        {
            "$limit": limit
        }
    ]

    listeners = listeners_col.aggregate(pipeline)
    return list(listeners)


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
                "genre": "$_id"
            }
        }
    ]

    genres = artists_col.aggregate(pipeline)
    return [doc["genre"] for doc in genres]

# ~~~~ Calculating Similarity ~~~~

# This is a very simple co-occurence technique that has limitations
# It counts the number of times artists appear together in listening history documents
# And returns the highest ones. 
# This isn't perfect because popular artists will tend to be ranked as more
# similar to all artists due to appearing in more listening histories

def get_similar_artists_simple(artist_name, limit = 10):
    pipeline = [
        {
        # limit search set to listener documents that contain artist
            "$match": {
                "listening_activity.artist_name": artist_name
            }

        },
        # undwind listening_activity so that each element of the list can be treated as
        # its own object
        {
            "$unwind": "$listening_activity"
        },

        # Remove the input artist from the count (before I did this the most similar artist was themselves)
        {
            "$match": {
                "listening_activity.artist_name":{"$ne":artist_name}
            }
        },
        # group by artists occurring in the same history, take the sum of when this happens
        {
            "$group": {
                "_id": {
                    "artist_mbid": "$listening_activity.artist_mbid",
                    "artist_name": "$listening_activity.artist_name"
                },
                "co_occ_count": {"$sum":1}
            }
        },
        # rank by the amount of times artists appear together
        {
            "$sort": {"co_occ_count": -1}
        },
        # return top # of similar artists
        {
            "$limit": limit
        },
        # convert the grouped artists back into a single artist list
        {
            "$project": {
                "_id": 0,
                "artist_name": "$_id.artist_name",
                "co_occ_count": 1
            }
        }
    ]

    return list(listeners_col.aggregate(pipeline))

def get_similar_artists_thru_genre(artist_name,limit=10):
  artist_doc = artists_col.find_one(
      {"name":artist_name},
      {"tag_counts.tag":1}
  )
  
  # build a set of the artists tags
  artist_tags = set(tag["tag"] for tag in artist_doc["tag_counts"])

  # Find artists that share at least one tag
  shared_artists = artists_col.find(
      {"name": {"$ne": artist_name}, 
       "tag_counts.tag": {"$in": list(artist_tags)}},
        {"name": 1, "country": 1, "tag_counts.tag": 1}
  )

  similar_artists = []

  for shared_artist in shared_artists:
    shared_artist_tags = set(tag["tag"] for tag in artist_doc["tag_counts"])
    set_intersection = len(shared_artist_tags & artist_tags)
    similar_artists.append({
        "artist_name": shared_artist["name"],
        "shared_tag_count": set_intersection
    })
  similar_artists.sort(key=lambda x: x["shared_tag_count"], reverse=True)
  return similar_artists[:limit]
