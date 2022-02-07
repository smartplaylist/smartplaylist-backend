# spotify-grabtrack

## Usage

### Build application image

1. `docker build -t grabtrack-app .`
1. `docker run -ti --rm -v $(pwd)/src:/usr/src/app --name app grabtrack-app`
1. `docker run -ti --rm -v $(pwd)/src:/usr/src/app --name app grabtrack-app sh --login`

### Run the stack

1. `docker-compose -f stack.yml up` add `-d` to run in the background
1. Open database UI: `http://localhost:8080/?pgsql=db&username=postgres`
1. Open RabbitMQ UI: `http://localhost:15672/`
