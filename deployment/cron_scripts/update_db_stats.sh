#!/bin/bash

NOW=$(date '+%Y-%m-%d-%H%M%S')
echo $NOW "Updating db stats"

docker run --rm --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env app:current pipenv run python update_db_stats.py


