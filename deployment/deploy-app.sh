#!/bin/sh

WORKING_DIR=/home/www/spotify-grabtrack/

docker pull jkulak/grabtrack-app:latest
docker tag jkulak/grabtrack-app:latest app:current

docker stop albums_listener_1
docker run -d --rm --network my-bridge-network --env-file /home/www/spotify-grabtrack/.env --name albums_listener_1 app:current pipenv run python get_albums.py
docker stop albums_listener_2
docker run -d --rm --network my-bridge-network --env-file /home/www/spotify-grabtrack/.env --name albums_listener_2 app:current pipenv run python get_albums.py

docker stop album_details_listener_1
docker run -d --rm --network my-bridge-network --env-file /home/www/spotify-grabtrack/.env --name album_details_listener_1 app:current pipenv run python get_album_details.py

docker stop tracks_listener_1
docker run -d --rm --network my-bridge-network --env-file /home/www/spotify-grabtrack/.env --name tracks_listener_1 app:current pipenv run python get_track_details.py

docker rmi jkulak/grabtrack-app:latest
