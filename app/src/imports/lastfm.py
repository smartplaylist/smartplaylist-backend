import os

import pylast

LASTFM_API_KEY = os.environ["LASTFM_API_KEY"]
LASTFM_API_SECRET = os.environ["LASTFM_API_SECRET"]
LASTFM_USER = os.environ["LASTFM_USER"]
LASTFM_PASSWORD = os.environ["LASTFM_PASSWORD"]


def get_lastfm_network(cache_file=".cache-lastfm_api"):
    network = pylast.LastFMNetwork(
        api_key=LASTFM_API_KEY,
        api_secret=LASTFM_API_SECRET,
        username=LASTFM_USER,
        password_hash=pylast.md5(LASTFM_PASSWORD),
    )
    network.enable_caching(cache_file)
    network.enable_rate_limit()
    return network
