#!/bin/bash

NOW=$(date '+%Y-%m-%d-%H%M%S')
echo $NOW "Running Last.fm update script"

docker stop updater_lastfm_albums
docker rm updater_lastfm_albums
time docker run --name updater_lastfm_albums --network smartplaylist_network --env-file .env jkulak/smartplaylist-app pipenv run python update_get_album_lastfm_tags.py

docker stop updater_lastfm_artist
docker rm updater_lastfm_artist
time docker run --name updater_lastfm_artist --network smartplaylist_network --env-file .env jkulak/smartplaylist-app pipenv run python update_get_artist_lastfm_tags.py

docker stop updater_lastfm_track
docker rm updater_lastfm_track
time docker run --name updater_lastfm_track --network smartplaylist_network --env-file .env jkulak/smartplaylist-app pipenv run python update_get_track_lastfm_tags.py
