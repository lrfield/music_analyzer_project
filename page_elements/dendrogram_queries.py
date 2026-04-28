from vis_utils.dendrogram import plot_dendrogram
from vis_utils.image_conversion import convert_matplot_fig_to_image
from vis_utils.cache import save_file_to_cache, read_file_from_cache, save_json_to_cache, read_json_from_cache
from mongodb_queries.db_constants import db, artists_col, genres_col, listeners_col
from mongodb_queries.genre_col_queries import get_genres
import pandas as pd
import matplotlib as plt


def plot_genre_dendrogram(limit=100):
    print("plot genre dendogram called")

    dendrogram_file = read_file_from_cache('dendrogram_cache', f"dendrogram_{limit}")
    if(dendrogram_file):
        print("Returning locally computed dendrogram stored in static")
        return dendrogram_file
    
    # grab a list of genre docs using the db.py function
    genres = get_genres(limit)
    
    # turn it into a list of only names
    genre_list = [genre["_id"] for genre in genres]

    # intialize the matrix as a symmetrical grid with identical genre cols and rows
    co_occ_matrix = {col_genre: {row_genre: 0 for row_genre in genre_list} for col_genre in genre_list}
    print("successfully initialized co-occ-matrix")
    # Work thru the list one genre at a time
    for genre in genre_list:
        pipeline = [
            # Find artists that have this genre
            {
                "$match": {
                    "tag_counts.tag": genre
                }
            },
            # unwind to get individual objects of artist-tag_counts
            {
                "$unwind": "$tag_counts"
            },
            # find artists-tag pairs remaining that also have tags in the rest of the list
            # drop the artist-tag pairs of the currently inspected genres (not needed, will always be coocurrent with itself)
            {
                "$match": {
                    "tag_counts.tag": {
                        "$in": genre_list,
                        "$ne": genre
                    }
                }
            },
            # Use group to sum a how many pairs occur for each genre in the rest of the list
            # use tag_count to weight by certainty of votes
            # NOTE: This may introduce bias of some kind. More popular artists have more votes in general
            # However, I tried just summing occurences too (using 1 as the arg for sum) and this produces more
            # logical dendrograms
            {
                "$group": {
                    "_id": "$tag_counts.tag",
                    "co_occ_count": {"$sum": "$tag_counts.count"}
                }
            },
            # Use project to only return relevant fields, rename _id as genre
            {
                "$project": {
                    "_id": 0,
                    "genre": "$_id",
                    "co_occ_count": 1
                }
            }
        ]

        # we end up with a list of co-occurency scores against the currently analyzed genre for every other genre in the list
        co_occ_col = list(artists_col.aggregate(pipeline))

        # Insert this list as a column based on the analyzed genres position in the list into the co-occurency matrix
        for row in co_occ_col:
            co_genre = row["genre"]
            count = row["co_occ_count"]
            co_occ_matrix[genre][co_genre] = count

    # convert matrix to dataframe
    df = pd.DataFrame(co_occ_matrix).T
    print("successfully finished co-occ-matrix")
    fig, ax = plot_dendrogram(df)
    print("successfully plotting dendrogram")
    
    dendrogram_file = convert_matplot_fig_to_image(fig)
    plt.close(fig)
    print("Saving result to cache in static")
    save_file_to_cache('dendrogram_cache', f"dendrogram_{limit}", dendrogram_file)

    return dendrogram_file