#!/bin/bash

NOW=$(date '+%Y-%m-%d-%H%M%S')
echo $NOW "Running update script"

docker run --rm --network my-bridge-network --env-file /home/www/spotify-grabtrack/.env app:current pipenv run python update.py
docker start tracks_listener_1
docker start tracks_listener_2
