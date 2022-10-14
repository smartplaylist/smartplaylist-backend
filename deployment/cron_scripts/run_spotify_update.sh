#!/bin/bash

NOW=$(date '+%Y-%m-%d-%H%M%S')
echo $NOW "Running update script"

docker run --rm --network my-bridge-network --env-file /home/www/spotify-grabtrack/.env app:current pipenv run python update.py

docker start albums_listener_1
docker start albums_listener_2
docker start albums_listener_3
docker start albums_listener_4
docker start albums_listener_5
docker start albums_listener_6
docker start albums_listener_7
docker start albums_listener_8
docker start albums_listener_9
docker start albums_listener_10
docker start albums_listener_11
docker start albums_listener_12

docker start album_details_listener_1
docker start album_details_listener_2
docker start album_details_listener_3

docker start tracks_listener_1
docker start tracks_listener_2
