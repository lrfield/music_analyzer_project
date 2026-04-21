import pymongo
import os
from mongodb_queries.db_constants import listeners_col

# This module contains the queries that access the listener_profile collection in the music
# database.

# IMPORTANT: The keys for the elements of returned dict elements from queries are essential
# For the hyperlinking html code to work. templates/list_table_macro.html generates links based on key names.

# return a listener doc from a username
def get_listener(_id):
    doc = listeners_col.find_one({"_id": _id})
    return doc

def get_total_num_listeners():
    return listeners_col.count_documents({})

def get_total_play_count_for_listener(_id):
    doc = listeners_col.find_one(
        {"_id": _id},
        {"total_play_count": 1, "_id": 0}
    )
    if not doc:
        return None
    return doc["total_play_count"]

# Get a list of all the artist names that a listener has in their listening_history
def get_artist_names_for_listener(_id):
    doc = listeners_col.find_one(
        {"_id": _id},
        {"listening_activity.artist_name": 1, "_id": 0}
    )
    if not doc:
        return None
    return [entry["artist_name"] for entry in doc["listening_activity"]]

# Return a number for a given listener username corresponding to their place in 
# the listener collection when it is sorted by the total_play_count_field (their rank)
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

# Get the list of listeners in the collection sorted by total_play_count
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
                "listener_name": "$_id",
                "total_play_count": 1
            }
        }
    ]

    listeners = listeners_col.aggregate(pipeline)
    return list(listeners)

# Trickier than you would think!
# the fact that listening activity is a nested list makes this a little more annoying

# Find listener docs that have this artist in their history
# seperate their listening history into individual listener-artist pairs
# Use match again to throw away all of the other listener-artist pairs from the listener's history
# only "artist_name"-listener pairs persist
# Then use project to make new objects consisting of the listener names, count, and artist names
# Then sort by listen count and limit the returned amount.
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
                "listener_name": "$_id",
                "listen_count": "$listening_activity.listen_count",
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
                "co-occurence_count": {"$sum":1}
            }
        },
        # rank by the amount of times artists appear together

        {
            "$sort": {"co-occurence_count": -1}
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
                "co-occurence_count": 1
            }
        }
    ]

    return list(listeners_col.aggregate(pipeline))