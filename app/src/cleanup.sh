#!/bin/sh

docker run -ti -v $(pwd)/db:/db --rm --network spotify-grabtrack_default alembic-image alembic downgrade base
docker run -ti -v $(pwd)/db:/db --rm --network spotify-grabtrack_default alembic-image alembic upgrade
docker run -ti --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python delete_queues.py
