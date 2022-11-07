#!/bin/bash

ENV_FILE=/home/www/spotify-grabtrack/.env

NOW=$(date '+%Y-%m-%d-%H%M%S')
echo $NOW "Running Last.fm update script"

docker run --rm --network smartplaylist_network --env-file $ENV_FILE app:current pipenv run python feed_tracks_to_have_tags_updated.py

docker stop listener_compute_track_genres
docker rm listener_compute_track_genres
docker run --name listener_compute_track_genres --network smartplaylist_network --env-file $ENV_FILE jkulak/smartplaylist-app pipenv run python listener_compute_track_genres.py

