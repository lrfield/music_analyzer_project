import pymongo
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://fieldl_db_user:JcktLsFY2DeFl9za@maincluster.gy24md4.mongodb.net/")
DB_NAME   = "music_data"

# Single client instance reused across requests
client = pymongo.MongoClient(MONGO_URI)
db     = client[DB_NAME]

artists_col = db["artists"]
genres_col  = db["genre_profiles"]


def get_countries():
    countries = artists_col.distinct("country")
    # distinct() can return None if a document has no country field
    return sorted([c for c in countries if c])


def get_genres():
    genres = genres_col.distinct("_id")
    return sorted([g for g in genres if g])


def top_artists_in_country(country, limit=10):
    cursor = (
        artists_col
        .find({"country": country}, {"name": 1})
        .sort("total_listen_count", pymongo.DESCENDING)
        .limit(limit)
    )
    return [doc["name"] for doc in cursor]


def top_genres_in_country(country, limit=10):
    results = []

    for genre_doc in genres_col.find({}):
        genre_name    = genre_doc["_id"]
        top_countries = genre_doc.get("top_countries", [])

        # Find this country's listen count within the genre's top_countries list
        country_entry = next(
            (entry for entry in top_countries if entry["country"] == country),
            None
        )

        if country_entry:
            results.append({
                "genre":        genre_name,
                "listen_count": country_entry["listen_count"]
            })

    # Sort by listen count descending and return genre name strings
    results.sort(key=lambda x: x["listen_count"], reverse=True)
    return [r["genre"] for r in results[:limit]]