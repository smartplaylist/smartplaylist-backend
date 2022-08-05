import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
result = sp.audio_features(tracks=["1tkkrLY3upIwNfLs4ei8Bh"])
