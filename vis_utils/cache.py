import os, hashlib
import json

# I found that caching some graphs (especially dendrograms) was very necessary
# they use enough memory to crash the website
# not caching by instance, I'm computing locally, storing in the static folder,
# then updating manually via github release.

# copying this code to create cache functions https://shawnway210.hashnode.dev/caching-in-python
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'static')

def save_file_to_cache(cache_folder, cache_filename, file):
    cache_path = os.path.join(CACHE_DIR, cache_folder, f"{cache_filename}.b64")
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(cache_path, "w") as f:
        f.write(file)

def read_file_from_cache(cache_folder, cache_filename):
    cache_path = os.path.join(CACHE_DIR, cache_folder, f"{cache_filename}.b64")
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            return f.read()
    else:
        return False
    
def save_json_to_cache(cache_folder, cache_filename, data):
    cache_path = os.path.join(CACHE_DIR, cache_folder)
    os.makedirs(cache_path, exist_ok=True)
    file_path = os.path.join(cache_path, f"{cache_filename}.json")
    with open(file_path, 'w') as f:
        json.dump(data, f)

def read_json_from_cache(cache_folder, cache_filename):
    file_path = os.path.join(CACHE_DIR, cache_folder, f"{cache_filename}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        return json.load(f)