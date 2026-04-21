# THESE ARE NOT FOR USING IN ANY FUNCTIONAL WAY

# these dicts are just for the drop-down element on the page
# to describe what pipeline query was used to make an element

# This is a really annoying way to do this that requires manual updating
# But I dont want to do an object oriented thing to make all of the actual db
# functions draw from a dict like thus, plus I think it would be very confusing to follow
query_display_list = {
    # ~~~~ Simple field retrieval functions ~~~~
    "get_artist": {
        "mongo_arg": {"name": "[name]"},
        "mongo_function": "db.artists.find_one()"
    },
    "get_listener": {
        "mongo_arg": {"_id": "[_id]"},
        "mongo_function": "db.listeners.find_one()"
    },
    "get_genre": {
        "mongo_arg": {"_id": "[_id]"},
        "mongo_function": "db.genre_profiles.find_one()"
    },
    "get_countries": {
        "mongo_arg": "country",
        "mongo_function": "db.artists.distinct()"
    },
    "get_color_for_tags": {
        "mongo_arg": [{}, {"assigned_color": 1}],
        "mongo_function": "db.genre_profiles.find()"
    },
    "get_total_num_artists": {
        "mongo_arg": {},
        "mongo_function": "db.artists.count_documents()"
    },
    "get_total_num_listeners": {
        "mongo_arg": {},
        "mongo_function": "db.listeners.count_documents()"
    },
    "get_total_num_genres": {
        "mongo_arg": {},
        "mongo_function": "db.genre_profiles.count_documents()"
    },
    "get_num_artists_in_genre": {
        "mongo_arg": {"tag_counts.tag": "[genre]"},
        "mongo_function": "db.artists.count_documents()"
    },
    "get_total_play_count_for_listener": {
        "mongo_arg": [{"_id": "[_id]"}, {"total_play_count": 1, "_id": 0}],
        "mongo_function": "db.listeners.find_one()"
    },
    "get_artist_names_for_listener": {
        "mongo_arg": [{"_id": "[_id]"}, {"listening_activity.artist_name": 1, "_id": 0}],
        "mongo_function": "db.listeners.find_one()"
    },
 
    # ~~~~ Ranking Functions ~~~~
    "get_listener_rank_by_play_count": {
        "mongo_arg": [
            [{"_id": "[_id]"}, {"total_play_count": 1}],
            {"total_play_count": {"$gt": "[listener_play_count]"}}
        ],
        "mongo_function": "db.listeners.find_one()\ndb.listeners.count_documents()"
    },
    "get_genre_rank_by_unique_listeners": {
        "mongo_arg": [
            [{"_id": "[_id]"}, {"total_unique_listeners": 1}],
            {"total_unique_listeners": {"$gt": "[genre_listener_count]"}}
        ],
        "mongo_function": "db.genre_profiles.find_one()\ndb.genre_profiles.count_documents()"
    },
    "get_artist_rank_by_unique_listeners": {
        "mongo_arg": [
            [{"name": "[name]"}, {"unique_listeners": 1}],
            {"unique_listeners": {"$gt": "[artist_listener_count]"}}
        ],
        "mongo_function": "db.artists.find_one()\ndb.artists.count_documents()"
    },
 
    # ~~~~ Getting a Sorted List of Items ~~~~
    "get_top_artists": {
        "mongo_arg": [
            {
                "$sort": {
                    "unique_listeners": -1
                }
            },
            {
                "$limit": "[limit]"
            },
            {
                "$project": {
                    "_id": 0,
                    "artist_name": "$name",
                    "country": 1,
                    "unique_listeners": 1,
                    "genre_tags": "$tag_counts"
                }
            }
        ],
        "mongo_function": "db.artists.aggregate()"
    },
    "get_all_artists": {
        "mongo_arg": [
            {
                "$sort": {
                    "unique_listeners": -1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "artist_name": "$name",
                    "country": 1,
                    "unique_listeners": 1,
                    "genre_tags": "$tag_counts"
                }
            }
        ],
        "mongo_function": "db.artists.aggregate()"
    },
    "top_artists_for_genre": {
        "mongo_arg": [
            {
                "$match": {
                    "tag_counts.tag": "[genre]"
                }
            },
            {
                "$sort": {
                    "unique_listeners": -1
                }
            },
            {
                "$limit": "[limit]"
            },
            {
                "$project": {
                    "_id": 0,
                    "artist_name": "$name",
                    "play_count": 1,
                    "unique_listeners": 1,
                    "country": 1
                }
            }
        ],
        "mongo_function": "db.artists.aggregate()"
    },
    "top_artists_in_country": {
        "mongo_arg": [
            {
                "$match": {
                    "country": "[country]"
                }
            },
            {
                "$sort": {
                    "play_count": -1
                }
            },
            {
                "$limit": "[limit]"
            },
            {
                "$project": {
                    "name": 1
                }
            }
        ],
        "mongo_function": "db.artists.aggregate()"
    },
    "get_top_listeners": {
        "mongo_arg": [
            {
                "$sort": {
                    "total_play_count": -1
                }
            },
            {
                "$limit": "[limit]"
            },
            {
                "$project": {
                    "_id": 1,
                    "total_play_count": 1
                }
            }
        ],
        "mongo_function": "db.listeners.aggregate()"
    },
    "get_genres": {
        "mongo_arg": [
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
                "$limit": "[limit]"
            },
            {
                "$project": {
                    "genre_name": "$_id",
                    "total_unique_listeners": 1
                }
            }
        ],
        "mongo_function": "db.genre_profiles.aggregate()"
    },
    "top_genres_in_country": {
        "mongo_arg": [
            {
                "$unwind": "$top_countries"
            },
            {
                "$match": {
                    "top_countries._id": "[country]"
                }
            },
            {
                "$sort": {
                    "top_countries.unique_listeners": -1
                }
            },
            {
                "$limit": "[limit]"
            },
            {
                "$project": {
                    "_id": 0,
                    "genre": "$_id",
                    "unique_listeners": "$top_countries.unique_listeners"
                }
            }
        ],
        "mongo_function": "db.genre_profiles.aggregate()"
    },
    "get_listeners_of_artist": {
        "mongo_arg": [
            {
                "$match": {
                    "listening_activity.artist_name": "[artist_name]"
                }
            },
            {
                "$unwind": "$listening_activity"
            },
            {
                "$match": {
                    "listening_activity.artist_name": "[artist_name]"
                }
            },
            {
                "$project": {
                    "listener_name": "$_id",
                    "listen_count": "$listening_activity.listen_count",
                    "artist_name": "$listening_activity.artist_name"
                }
            },
            {
                "$sort": {"artist_listen_count": -1}
            },
            {
                "$limit": "[limit]"
            }
        ],
        "mongo_function": "db.listeners.aggregate()"
    },
    "get_genres_for_listener": {
        "mongo_arg": [
            {
                "$match": {
                    "name": {"$in": "[artist_names]"}
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
        ],
        "mongo_function": "db.artists.aggregate() (artist_names grabbed from listening activity)"
    },
 
    # ~~~~ Calculating Similarity ~~~~
    "get_similar_artists_simple": {
        "mongo_arg": [
            {
                "$match": {
                    "listening_activity.artist_name": "[artist_name]"
                }
            },
            {
                "$unwind": "$listening_activity"
            },
            {
                "$match": {
                    "listening_activity.artist_name": {"$ne": "[artist_name]"}
                }
            },
            {
                "$group": {
                    "_id": {
                        "artist_mbid": "$listening_activity.artist_mbid",
                        "artist_name": "$listening_activity.artist_name"
                    },
                    "co-occurence_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"co-occurence_count": -1}
            },
            {
                "$limit": "[limit]"
            },
            {
                "$project": {
                    "_id": 0,
                    "artist_name": "$_id.artist_name",
                    "co-occurence_count": 1
                }
            }
        ],
        "mongo_function": "db.listeners.aggregate()"
    },
    "get_similar_genres_simple": {
        "mongo_arg": [
            {
                "$match": {
                    "tag_counts.tag": "[genre_name]"
                }
            },
            {
                "$unwind": "$tag_counts"
            },
            {
                "$match": {
                    "tag_counts.tag": {"$ne": "[genre_name]"}
                }
            },
            {
                "$group": {
                    "_id": "$tag_counts.tag",
                    "co-occurence_count": {"$sum": "$tag_counts.count"}
                }
            },
            {
                "$sort": {"co-occurence_count": -1}
            },
            {
                "$limit": "[limit]"
            },
            {
                "$project": {
                    "_id": 0,
                    "genre_name": "$_id",
                    "co-occurence_count": 1
                }
            }
        ],
        "mongo_function": "db.artists.aggregate()"
    },
 
    # ~~~~ Visualization functions ~~~~
 
    # MAP FUNCTIONS
 
    "plot_artist_origin_by_country_with_genre": {
        "mongo_arg": [
        {
            "$match":{
                "country": {"$exists": True, "$ne": None},
                "tag_counts.tag": "[tag]"
            } 
 
        },
        {
            "$sort": {"unique_listeners": -1}
        },
        {
            "$group": {
                "_id": "$country",
                "name":{"$first":"$name"},
                "unique_listeners":{"$first":"$unique_listeners"}
            }
        },
        {
            "$sort": {"_id": 1}
        },
        {
            "$project":{
                "country": "$_id",
                "artist_name":"$name",
                "unique_listeners": 1
            }
        }
        ],
        "mongo_function": "db.artists.aggregate()"  
    },
 
    "plot_artist_origin_by_country_no_genre": {
        "mongo_arg": [
        {
            "$match":{
                "country": {"$exists": True, "$ne": None}
            } 
 
        },
        {
            "$sort": {"unique_listeners": -1}
        },
        {
            "$group": {
                "_id": "$country",
                "name":{"$first":"$name"},
                "unique_listeners":{"$first":"$unique_listeners"}
            }
        },
        {
            "$sort": {"_id": 1}
        },
        {
            "$project":{
                "country": "$_id",
                "artist_name":"$name",
                "unique_listeners": 1
            }
        }
        ],
        "mongo_function": "db.artists.aggregate()"  
    },
 
    "plot_genre_origin_by_country": {
        "mongo_arg": [
        {
            "$unwind": "$top_countries"
        },
        {
            "$project": {
                "genre_name":         "$_id",
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
        ],
        "mongo_function": "db.genre_profiles.aggregate()"  
    },
 
    # BAR PLOT FUNCTIONS
    "plot_artists_origin_by_year_with_genre": {
        "mongo_arg": [
        {
            "$match":{
                "begin_year": {"$exists": True, "$ne": None},
                "tag_counts.tag": "[tag]"
            }
        },
        {"$sort": {
            "begin_year": 1, 
            "unique_listeners": -1
            }
        },
        {
            "$group": {
                "_id": "$begin_year",
                "artist_name": {"$first": "$name"},
                "unique_listeners": {"$first": "$unique_listeners"},
                "main_genre": {"$first": {"$arrayElemAt": ["$tag_counts.tag", 0]}}
            }
        },
        {
            "$sort": {"_id": 1}
        },
        {
            "$project":{
                "begin_year": "$_id",
                "artist_name": 1,
                "unique_listeners": 1,
                "main_genre": 1
            }
        }
        ],
        "mongo_function": "db.artists.aggregate()"  
    },
 
    "plot_artists_origin_by_year_no_genre": {
        "mongo_arg": [
        {
            "$match":{
                "begin_year": {"$exists": True, "$ne": None},
            }
        },
        {"$sort": {
            "begin_year": 1, 
            "unique_listeners": -1
            }
        },
        {
            "$group": {
                "_id": "$begin_year",
                "artist_name": {"$first": "$name"},
                "unique_listeners": {"$first": "$unique_listeners"},
                "main_genre": {"$first": {"$arrayElemAt": ["$tag_counts.tag", 0]}}
            }
        },
        {
            "$sort": {"_id": 1}
        },
        {
            "$project":{
                "begin_year": "$_id",
                "artist_name": 1,
                "unique_listeners": 1,
                "main_genre": 1
            }
        }
        ],
        "mongo_function": "db.artists.aggregate()"  
    },
 
    "plot_genre_by_year": {
        "mongo_arg": [
        {
            "$match": {
                "begin_year": {"$exists": True, "$ne": None},
                "tag_counts.tag": {"$exists": True, "$ne": []}
            }
        },
        {
            "$unwind": "$tag_counts"
        },
        {
            "$group": {
                "_id": {
                    "begin_year": "$begin_year",
                    "tag": "$tag_counts.tag"
                }, 
                "unique_listeners": {
                    "$sum": "$unique_listeners"
                }
            }
        },
        {
            "$sort": {
                "_id.begin_year": 1,
                "unique_listeners": -1
            }
        },        
        {
            "$group": {
                "_id": "$_id.begin_year",
                "genre": {"$first": "$_id.tag"},
                "unique_listeners": {"$first": "$unique_listeners"}
            }
        },
        {
            "$sort": {"_id": 1}
        },
        {
            "$project":{
                "begin_year": "$_id",
                "genre_name": "$genre",
                "unique_listeners": 1
            }
        }
        ],
        "mongo_function": "db.artists.aggregate()"  
    },
 
    # PIE CHART FUNCTIONS
    "artist_genre_tag_pie_chart": {
        "mongo_arg": [
            {"name": "[name]"},
            {"_id":0, "name":1,"tag_counts":1}
        ],
        "mongo_function": "db.artists.find_one()"  
    },
    "genre_country_pie_chart": {
        "mongo_arg": [
            {"_id": "[name]"},
            {"_id":1, "top_countries":1}
        ],
        "mongo_function": "db.genre_profiles.find_one()"  
    },
    "genre_artist_pie_chart": {
        "mongo_arg": [
            {"_id": "[name]"},
            {"_id":1, "top_artists":1}
        ],
        "mongo_function": "db.genre_profiles.find_one()"  
    },
    "listener_artist_pie_chart": {
        "mongo_arg": [
            {"_id": "[name]"},
            {"_id":1, "listening_activity":1}
        ],
        "mongo_function": "db.listeners.find_one()"  
    },
    "plot_dendrogram": {
        "mongo_arg": [
            {
                "$match": {
                    "tag_counts.tag": "[genre_for_loop_iter]"
                }
            },
            {
                "$unwind": "$tag_counts"
            },
            {
                "$match": {
                    "tag_counts.tag": {
                        "$in": "genre_list",
                        "$ne": "[genre_for_loop_iter]"
                    }
                }
            },
            {
                "$group": {
                    "_id": "$tag_counts.tag",
                    "co_occ_count": {"$sum": "$tag_counts.count"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "genre": "$_id",
                    "co_occ_count": 1
                }
            }
        ],
        "mongo_function": "artists_col.aggregate(pipeline) \nto get one column, loop for every genre in list, \nstore in co-occurence matrix"
        }
}