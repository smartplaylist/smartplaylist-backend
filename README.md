# spotify-grabtrack

## Usage

1. `cp .env-template .env` and edit environment variables (add Spotify credentials)
1. Run the stack `docker-compose -f stack.yml up`
1. Access Admier: <http://localhost:8080/?pgsql=db&username=postgres>
1. Open RabbitMQ GUI: <http://localhost:15672/>. Default credentials are `guest`/`guest`
1. Open the web app: <http://localhost:3001/>

It will run Postgres, Rabbit, REST API server, web app and a Python data grabbing script. Python will try to grab data before database is available so give it a few seconds and run `docker start spotify-grabtrack-app-1` it will grab data from Spotify API and save it to the database.

Check the data here: <http://localhost:8080/?pgsql=db&username=postgres&db=spotify&ns=public&select=tracks>

## Work with alembic (database migrations)

1. Have the stack working (you need a running database) `docker-compose -f stack.yml up -d`
1. `docker build -t alembic-image ./db`
1. Run migrations `docker run -ti -v $(pwd)/db:/db --rm --network spotify-grabtrack_default alembic-image alembic upgrade head`
1. Undo last migration `docker run -ti -v $(pwd)/db:/db --rm --network spotify-grabtrack_default alembic-image alembic downgrade -1`

## Running the listeners

Listeners are checking for Rabbit messages and downloading arist, alubm and track data from Spotify.

1. Get followed artists `docker run -ti --rm --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env spotify-grabtrack_app pipenv run python get_followed_artists.py`
1. Get albums `docker run -ti --rm --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env spotify-grabtrack_app pipenv run python get_albums.py`
1. Get album details `docker run -ti --rm --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env spotify-grabtrack_app pipenv run python get_album_details.py`
1. Get track details `docker run -ti --rm --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env spotify-grabtrack_app pipenv run python get_track_details.py`

## Get oAuth token

After running `get_followed_artists.py` you will be asked to open an URL and paste the URL you were redirected to to obtain the oAuth token.

## API (using PostgREST)

After running the stack, API will be available at: <http://127.0.0.1:3000/tracks?main_artist=eq.Devlin>

Usage and documentation: <https://postgrest.org/en/stable/api.html#operators>

## WWW (working with the web app)

After building the stack, run

- `docker run -ti --rm --network spotify-grabtrack_default -p 3001:3001 -v $(pwd)/www/app/src:/app/src --env-file .env --name www spotify-grabtrack_www sh --login` to enter the www container
- `yarn start` to start the web server. On MacOS starting might take >30 seconds due to slow Docker mounts.
- Open the app in your browser <http://localhost:3001/>

## Other

- Test application code: `docker run -ti --rm --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env --name app spotify-grabtrack_app sh --login`
- Enter application container `docker run -ti --rm --network spotify-grabtrack_default -v $(pwd)/app/src:/app --env-file .env spotify-grabtrack_app sh --login`
- Inside the container `pipenv run python get_followed_artists.py`
