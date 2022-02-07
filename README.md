# spotify-grabtrack

## Usage

1. `mv stack.yml-template stack.yml` and edti environment variables
1. Build the application image `docker build -t grabtrack-app .`
1. Run the whole stack `docker-compose -f stack.yml up`
1. Access Admier: <http://localhost:8080/?pgsql=db&username=postgres>
1. Open RabbitMQ GUI: <http://localhost:15672/>

It will run Postgres, Rabbit and a Python script. Python will try to grab data before database is available so give it a few seconds and run `docker start spotify-grabtrack-app-1` it will grab data from Spotify API and save it to the database.

Check the data here: <http://localhost:8080/?pgsql=db&username=postgres&db=spotify&ns=public&select=tracks>

## Other

1. Enter application container `docker run -ti --rm -v $(pwd)/app:/usr/src/app --name app grabtrack-app sh --login`
