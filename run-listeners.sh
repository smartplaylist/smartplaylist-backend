#!/bin/bash

(trap 'kill 0' SIGINT;
docker run -ti --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_albums.py &
docker run -ti --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_albums.py &
docker run -ti --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_album_details.py &
docker run -ti --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_album_details.py &
docker run -ti --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_track_details.py
)
