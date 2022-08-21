import requests_cache
from requests_cache import SQLiteCache

requests_cache.install_cache(
    "grabtrack_sqlite_cache", SQLiteCache("spotify_api_cache", timeout=30)
)
