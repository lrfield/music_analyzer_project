from vis_utils.bar_plot import plot_bar
from vis_utils.image_conversion import convert_matplot_fig_to_image
from vis_utils.cache import save_file_to_cache, read_file_from_cache, save_json_to_cache, read_json_from_cache
from mongodb_queries.db_constants import db, artists_col, genres_col, listeners_col
from mongodb_queries.genre_col_queries import get_color_for_tags

def plot_artists_origin_by_year(tag=None):

    # try to retrieve cached bar plot for commonly repeated query: origin by year without tag
    if(tag == None):
        artist_bar_plot_file = read_file_from_cache('bar_plot_cache', "artist_bar_plot_no_tag")
        binned_year_artists  = read_json_from_cache('bar_plot_cache', "artist_bar_plot_no_tag_list")
        if((artist_bar_plot_file != None) and (binned_year_artists != None)):
            print("Returning locally computed artist origin bar plot (no tags) stored in static")
            return artist_bar_plot_file, binned_year_artists
    

    # The filtering section/$match stage has to be constructed seperately
    # This is because I wanted to have the default call to the function graph
    # without filtering by genre tags.
    # There is no way to do that without appending the tag filter outside of the pipeliene (at least that I know of)
    filter_section = {
        "begin_year": {"$exists": True, "$ne": None}
    }

    if tag is not None:
        filter_section["tag_counts.tag"] = tag

    pipeline = [
        {
            # filter out artists that dont have the begin_year field filled out
            "$match": filter_section
        },
        # sort artists by beginning year ascending, then within each year, by unique listeners count descending
        {"$sort": {
            "begin_year": 1, 
            "unique_listeners": -1
            }
        },
        {
            # group artists by begin year, then only save the highest unique listeners (the first that appears since its sorted)
            "$group": {
                "_id": "$begin_year",
                "artist_name": {"$first": "$name"},
                "unique_listeners": {"$first": "$unique_listeners"},
                "main_genre": {"$first": {"$arrayElemAt": ["$tag_counts.tag", 0]}} # save main genre for coloring
            }
        },
            # re-sort by begin_year (grouping removes sorting)
        {
            "$sort": {"_id": 1}
        },
        {
            "$project":{
                "begin_year": "$_id", # rename _id to begin_year
                "artist_name": 1,
                "unique_listeners": 1,
                "main_genre": 1 
            }
        }
    ]

    # run the collection through the pipeling
    binned_year_artists = list(artists_col.aggregate(pipeline))

    if not binned_year_artists:
        return None
    
    # convert the pipeline results into the format needed for the bar plot function
    data = [
        {
            "category": str(year["begin_year"]),
            "value": year["unique_listeners"],
            "label": f"{year["artist_name"]} - {year.get("main_genre")}" ,
            "main_genre": year.get("main_genre")
        }
        for year in binned_year_artists
    ]
    # get the dict of tag colors for coloring bars individually
    tag_colors = get_color_for_tags()

    # Plot the data
    fig, ax = plot_bar(
        data=data,
        x_axis_title="Unique Listeners",
        y_axis_title="Begin Year",
        bar_color="Black",
        figsize=(12, max(len(data) * 0.45,4)),
        bar_height=0.65,
        sort = False,
        bar_color_map = tag_colors,
        col_to_det_color = "main_genre"
    )
    artist_bar_plot_file = convert_matplot_fig_to_image(fig)
    # saving no tag case to cache
    if(tag == None):
        print("Saving result to cache in static")
        save_file_to_cache('bar_plot_cache', "artist_bar_plot_no_tag", artist_bar_plot_file)
        save_json_to_cache('bar_plot_cache', "artist_bar_plot_no_tag_list", binned_year_artists)

    return artist_bar_plot_file, binned_year_artists


def plot_genre_by_year():
    # try to read cached bar plot data 
    genre_bar_plot_file = read_file_from_cache('bar_plot_cache', "genre_bar_plot")
    sorted_genre_by_year = read_json_from_cache('bar_plot_cache', "genre_bar_plot_list")

    if((genre_bar_plot_file != None) and (sorted_genre_by_year != None)):
        print("Returning locally computed genre bar plot stored in static")
        return genre_bar_plot_file, sorted_genre_by_year
    

    pipeline = [
        {
            # filter out artists that dont have the begin_year field filled out
            "$match": {
                "begin_year": {"$exists": True, "$ne": None},
                # filter out artists that don't have a tag field
                "tag_counts.tag": {"$exists": True, "$ne": []}
            }
        },
        # expand the tags array
        {
            "$unwind": "$tag_counts"
        },

        # sum the total unique listener count for every instance of (year,genre) pair
        {
            "$group": {
                # create a new ID for every encountered pair of year and genre
                # so rock, 2011 is different than rock, 2012
                "_id": {
                    "begin_year": "$begin_year",
                    "tag": "$tag_counts.tag"
                }, 
                "unique_listeners": {
                    "$sum": "$unique_listeners"
                }
            }
        },
        # sort by unique listener count within years
        {
            "$sort": {
                "_id.begin_year": 1,
                "unique_listeners": -1
            }
        },

        # keep only the first encountered genre per year (since they are sorted this is the highest)
        
        {
            "$group": {
                "_id": "$_id.begin_year",
                "genre": {"$first": "$_id.tag"},
                "unique_listeners": {"$first": "$unique_listeners"}
            }
        },

        # Re-sort by year (grouping unsorts)
        {
            "$sort": {"_id": 1}
        },
        {
            "$project":{
                "begin_year": "$_id", # rename _id to begin_year
                "genre_name": "$genre",
                "unique_listeners": 1
            }
        }
    ]

    # run the collection through the pipeline
    sorted_genre_by_year = list(artists_col.aggregate(pipeline))

    if not sorted_genre_by_year:
        return None
    
    # convert the pipeline results into the format needed for the bar plot function
    data = [
        {"category": str(year["begin_year"]), "value": year["unique_listeners"], "label": year["genre_name"] }
        for year in sorted_genre_by_year
    ]

    # get the dict of tag colors for coloring bars individually
    tag_colors = get_color_for_tags()

    # Plot the data
    fig, ax = plot_bar(
        data=data,
        x_axis_title="Unique Listeners",
        y_axis_title="Begin Year",
        bar_color="Black",
        figsize=(12, len(data) * 0.45),
        bar_height=0.65,
        sort = False,
        bar_color_map = tag_colors,
        col_to_det_color = "label"
    )

    genre_bar_plot_file = convert_matplot_fig_to_image(fig)

    # saving bar plot to cache
    print("Saving result to cache in static")
    save_file_to_cache('bar_plot_cache', "genre_bar_plot", genre_bar_plot_file)
    save_json_to_cache('bar_plot_cache', "genre_bar_plot_list", sorted_genre_by_year)
    return genre_bar_plot_file, sorted_genre_by_year
