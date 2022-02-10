# spotify-grabtrack

## Usage

1. `cp stack.yml-template stack.yml` and edit environment variables (add Spotify credentials)
1. Run the stack `docker-compose -f stack.yml up`
1. Access Admier: <http://localhost:8080/?pgsql=db&username=postgres>
1. Open RabbitMQ GUI: <http://localhost:15672/>

It will run Postgres, Rabbit and a Python script. Python will try to grab data before database is available so give it a few seconds and run `docker start spotify-grabtrack-app-1` it will grab data from Spotify API and save it to the database.

Check the data here: <http://localhost:8080/?pgsql=db&username=postgres&db=spotify&ns=public&select=tracks>

## Work with alembic

1. Have the stack working (you need a running database) `docker-compose -f stack.yml up -d`
1. `docker build -t alembic-image ./db`
1. Run migrations `docker run -ti -v $(pwd)/db:/db --rm --network spotify-grabtrack_default alembic-image alembic upgrade head`

## Other

1. Enter application container `docker run -ti --rm -v $(pwd)/app:/usr/src/app --name app grabtrack-app sh --login`
