import os
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials

# CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
# CLIENT_SECRET = os.environ['SPOTIFY_CLIENT_SECRET']

# Uses SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET env vars
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

results = sp.search(q='weezer', limit=20)
for idx, track in enumerate(results['tracks']['items']):
    print(idx, track['name'])