#!/bin/sh

WORKING_DIR=/home/www/spotify-grabtrack/

SPOTIPY_CLIENT_ID_01=xxx
SPOTIPY_CLIENT_SECRET_01=xxx
SPOTIPY_CLIENT_ID_02=xxx
SPOTIPY_CLIENT_SECRET_02=xxx
SPOTIPY_CLIENT_ID_03=xxx
SPOTIPY_CLIENT_SECRET_03=xxx
SPOTIPY_CLIENT_ID_04=xxx
SPOTIPY_CLIENT_SECRET_04=xxx
SPOTIPY_CLIENT_ID_05=xxx
SPOTIPY_CLIENT_SECRET_05=xxx
SPOTIPY_CLIENT_ID_06=xxx
SPOTIPY_CLIENT_SECRET_06=xxx
SPOTIPY_CLIENT_ID_07=xxx
SPOTIPY_CLIENT_SECRET_07=xxx
SPOTIPY_CLIENT_ID_08=xxx
SPOTIPY_CLIENT_SECRET_08=xxx
SPOTIPY_CLIENT_ID_09=xxx
SPOTIPY_CLIENT_SECRET_09=xxx
SPOTIPY_CLIENT_ID_10=xxx
SPOTIPY_CLIENT_SECRET_10=xxx
SPOTIPY_CLIENT_ID_11=xxx
SPOTIPY_CLIENT_SECRET_11=xxx
SPOTIPY_CLIENT_ID_12=xxx
SPOTIPY_CLIENT_SECRET_12=xxx
SPOTIPY_CLIENT_ID_13=xxx
SPOTIPY_CLIENT_SECRET_13=xxx
SPOTIPY_CLIENT_ID_14=xxx
SPOTIPY_CLIENT_SECRET_14=xxx
SPOTIPY_CLIENT_ID_15=xxx
SPOTIPY_CLIENT_SECRET_15=xxx
SPOTIPY_CLIENT_ID_16=xxx
SPOTIPY_CLIENT_SECRET_16=xxx
SPOTIPY_CLIENT_ID_17=xxx
SPOTIPY_CLIENT_SECRET_17=xxx

# alembic upgrade head
# this needs either source code or an image with the source code
# docker run -ti -v $(pwd)/db:/db --rm --network smartplaylist_network alembic-image alembic upgrade head`

docker pull jkulak/smartplaylist-app:latest
docker tag jkulak/smartplaylist-app:latest app:current

# Run listeners

## get_albums
docker stop albums_listener_1
docker rm albums_listener_1
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_03 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_03 --name albums_listener_1 app:current pipenv run python get_albums.py
docker stop albums_listener_2
docker rm albums_listener_2
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_04 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_04 --name albums_listener_2 app:current pipenv run python get_albums.py
docker stop albums_listener_3
docker rm albums_listener_3
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_05 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_05 --name albums_listener_3 app:current pipenv run python get_albums.py
docker stop albums_listener_4
docker rm albums_listener_4
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_06 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_06 --name albums_listener_4 app:current pipenv run python get_albums.py
docker stop albums_listener_5
docker rm albums_listener_5
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_07 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_07 --name albums_listener_5 app:current pipenv run python get_albums.py
docker stop albums_listener_6
docker rm albums_listener_6
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_08 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_08 --name albums_listener_6 app:current pipenv run python get_albums.py
docker stop albums_listener_7
docker rm albums_listener_7
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_09 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_09 --name albums_listener_7 app:current pipenv run python get_albums.py
docker stop albums_listener_8
docker rm albums_listener_8
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_15 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_15 --name albums_listener_8 app:current pipenv run python get_albums.py
docker stop albums_listener_9
docker rm albums_listener_9
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_16 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_16 --name albums_listener_9 app:current pipenv run python get_albums.py
docker stop albums_listener_10
docker rm albums_listener_10
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_02 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_02 --name albums_listener_10 app:current pipenv run python get_albums.py

## get_album_details
docker stop album_details_listener_1
docker rm album_details_listener_1
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_10 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_10 --name album_details_listener_1 app:current pipenv run python get_album_details.py
docker stop album_details_listener_2
docker rm album_details_listener_2
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_11 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_11 --name album_details_listener_2 app:current pipenv run python get_album_details.py
docker stop album_details_listener_3
docker rm album_details_listener_3
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_12 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_12 --name album_details_listener_3 app:current pipenv run python get_album_details.py

## get_track_details
docker stop tracks_listener_1
docker rm tracks_listener_1
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_13 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_13 --name tracks_listener_1 app:current pipenv run python get_track_details.py
docker stop tracks_listener_2
docker rm tracks_listener_2
docker run -d --network smartplaylist_network --env-file /home/www/spotify-grabtrack/.env --env SPOTIPY_CLIENT_ID=$SPOTIPY_CLIENT_ID_14 --env SPOTIPY_CLIENT_SECRET=$SPOTIPY_CLIENT_SECRET_14 --name tracks_listener_2 app:current pipenv run python get_track_details.py


docker rmi jkulak/smartplaylist-app:latest
