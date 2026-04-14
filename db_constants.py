import os
import pymongo
MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://fieldl_db_user:JcktLsFY2DeFl9za@maincluster.gy24md4.mongodb.net/")
DB_NAME   = "music_data"

client = pymongo.MongoClient(MONGO_URI)
db     = client[DB_NAME]

artists_col = db["artists"]
genres_col  = db["genre_profiles"]
listeners_col  = db["listeners"]