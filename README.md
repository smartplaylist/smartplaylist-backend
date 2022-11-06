# spotify-grabtrack

## Usage

1. `cp .env-template .env` and edit environment variables
1. Run commands from `deployment/first_deployment.sh`
1. Access Admier: <http://localhost:8080/?pgsql=db&username=postgres>
1. Open RabbitMQ GUI: <http://localhost:15672/>. Default credentials are `guest`/`guest`
1. Open the web app: <http://localhost:3001/>

It will run Postgres, Rabbit, Redis for caching requests, RedisInsights for a GUI for Redis, a REST API server and a web app.

## Working with PostgreSQL

* Backup: `docker exec -ti spotify-grabtrack_db_1 pg_dump -U postgres -W -F c spotify -f /pg_backup/2022-03-31-backup.psql`
* Restore: `docker exec -ti spotify-grabtrack_db_1 pg_restore -U postgres -d spotify /pg_backup/2022-03-30-backup.psql`

Or

* Login to db Docker: `docker exec -ti spotify-grabtrack_db_1 bash --login`
* Backup database: `pg_dump -U postgres -W -F c spotify > /pgdata/2022-03-31-backup.psql`
* Restore: `pg_restore -U postgres -d pg_import_test /pgdata/2022-03-31-backup.psql`

### Rename database

1. `docker exec -ti spotify-grabtrack_db_1 bash --login`
1. `psql -U postgres`
1. `\connect postgres`
1. `ALTER DATABASE old_spotify RENAME TO spotify;`

## Work with alembic (database migrations)

1. Have the stack working (you need a running database) `docker-compose -f stack.yml up -d`
1. `docker build -t alembic-image ./db`
1. `docker run -ti -v $(pwd)/db:/db --rm --network smartplaylist_network alembic-image alembic revision -m "Create indexes on tracks"`
1. Run migrations `docker run -ti -v $(pwd)/db:/db --rm --network smartplaylist_network alembic-image alembic upgrade head`
1. Undo last migration `docker run -ti -v $(pwd)/db:/db --rm --network smartplaylist_network alembic-image alembic downgrade -1`

## Running the listeners

Listeners are checking for Rabbit messages and downloading artist, album and track data from Spotify API.

1. Get followed artists `docker run -ti --rm --network smartplaylist_network -p 8083:8083 -v $(pwd)/app/src:/app --env-file .env spotify-grabtrack_app pipenv run python get_followed_artists.py`
1. Run related artists listener: `docker run -ti --network smartplaylist_network -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_related_artists.py`
1. Get albums `docker run -ti --network smartplaylist_network -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_albums.py`
1. Get album details `docker run -ti --network smartplaylist_network -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_album_details.py`
1. Get track details `docker run -ti --network smartplaylist_network -v $(pwd)/app/src:/app --env-file .env --rm spotify-grabtrack_app pipenv run python get_track_details.py`

## Get oAuth token

After running `get_followed_artists.py` you will be asked to open an URL and paste the URL you were redirected to to obtain the oAuth token.

Remember, your Spotify Developer application in <https://developer.spotify.com/dashboard/applications> needs to have "Redirect URI" configured and same with `env SPOTIPY_REDIRECT_URI`

## API (using PostgREST)

After running the stack, API will be available at: <http://127.0.0.1:8081/tracks?main_artist=eq.Devlin>
