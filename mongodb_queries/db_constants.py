import os
import pymongo
MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is not set")


DB_NAME   = "music_data"

client = pymongo.MongoClient(MONGO_URI)
db     = client[DB_NAME]

artists_col = db["artists"]
genres_col  = db["genre_profiles"]
listeners_col  = db["listeners"]