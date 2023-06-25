#!/bin/bash

NOW=$(date '+%Y-%m-%d-%H%M%S')
echo $NOW "Monitoring broker"

docker run --rm --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env app:current pipenv run python monitor_broker.py


