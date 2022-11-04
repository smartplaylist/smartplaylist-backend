import spotipy

SPOTIPY_AUTH_CACHE_PATH = ".cache-spotipy"

sp = spotipy.Spotify(
    auth_manager=spotipy.SpotifyClientCredentials(
        cache_handler=spotipy.CacheFileHandler(
            cache_path=SPOTIPY_AUTH_CACHE_PATH
        )
    )
)
