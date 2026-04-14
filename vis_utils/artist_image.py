import requests

# https://developers.deezer.com/api/search/artist

def get_artist_image(artist_name):
    url = "https://api.deezer.com/search/artist"
    response = requests.get(url, params={"q": artist_name, "limit": 1})
    response.raise_for_status()
    data = response.json()

    if not data.get("data"):
        return None

    artist = data["data"][0]
    return artist.get("picture_xl")
