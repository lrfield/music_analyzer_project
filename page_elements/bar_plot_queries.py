from vis_utils.bar_plot import plot_bar
from vis_utils.image_conversion import convert_matplot_fig_to_image
from db_constants import db, artists_col, genres_col, listeners_col

def plot_artists_origin_by_year(tag=None):

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
                "name": {"$first": "$name"},
                "unique_listeners": {"$first": "$unique_listeners"}
            }
        },
            # re-sort by begin_year (grouping removes sorting)
        {
            "$sort": {"_id": 1}
        }
    ]

    # run the collection through the pipeling
    sorted_year_artists = list(artists_col.aggregate(pipeline))

    if not sorted_year_artists:
        return None
    
    # convert the pipeline results into the format needed for the bar plot function
    data = [
        {"category": str(year["_id"]), "value": year["unique_listeners"], "label": year["name"] }
        for year in sorted_year_artists
    ]

    # Plot the data
    fig, ax = plot_bar(
        data=data,
        x_axis_title="Unique Listeners",
        y_axis_title="Begin Year",
        highlight_color="Yellow",
        bar_color="Black",
        figsize=(12, len(data) * 0.45),
        bar_height=0.65,
        cutoff=None,
        sort = False
    )
    
    return convert_matplot_fig_to_image(fig)


def plot_genre_by_year():

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
        }
    ]

    # run the collection through the pipeline
    sorted_genre_by_year = list(artists_col.aggregate(pipeline))

    if not sorted_genre_by_year:
        return None
    
    # convert the pipeline results into the format needed for the bar plot function
    data = [
        {"category": str(year["_id"]), "value": year["unique_listeners"], "label": year["genre"] }
        for year in sorted_genre_by_year
    ]

    # Plot the data
    fig, ax = plot_bar(
        data=data,
        x_axis_title="Unique Listeners",
        y_axis_title="Begin Year",
        highlight_color="Yellow",
        bar_color="Black",
        figsize=(12, len(data) * 0.45),
        bar_height=0.65,
        cutoff=None,
        sort = False
    )

    return convert_matplot_fig_to_image(fig)
