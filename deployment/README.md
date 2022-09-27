# Installation

## Prepare production server

* `ssh-copy-id root@example.com`
* `ssh root@example.com`
* `adduser www`
* `usermod -aG sudo www`
* `sudo apt install docker.io`
* `sudo groupadd docker`
* `sudo usermod -aG docker $USER`
* `apt-get install webhook`

### First deployment

* make a copy of `.env` file from the repository and set variables
* `docker network create -d bridge my-bridge-network`
* `docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_db -v $(pwd)/pgdata:/pgdata --name db postgres:14.1-alpine`
* `docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_adminer -p 8081:8080 --name adminer adminer:4.8.1`
* `docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_broker -v $(pwd)/rabbitmq_mnesia_dir:/var/lib/rabbitmq/mnesia -p 15672:15672 -p 5672:5672 --name broker rabbitmq:3.9.13-management-alpine`
* `docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_api -p 3000:3000 --name api postgrest/postgrest:v10.0.0`

### Prepare new database

* `docker build -t alembic-image ./db`
* `docker run -ti -v $(pwd)/db:/db --rm --network my-bridge-network alembic-image alembic upgrade head`

### Import followed artists

* `docker build -t app ./app`
* `docker run -ti --rm --network my-bridge-network -p 8083:8083 -v $(pwd)/app/src:/app --env-file .env app pipenv run python sync_followed_artists.py`

#### Run www

* `docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_www -p 3001:3001 --name www jkulak/grabtrack-www:latest`

#### Run listeners

* `docker run -d --rm --network my-bridge-network --env-file .env app pipenv run python get_albums.py`

* `sudo apt-get install webhook`
* `cat webhook.service > /lib/systemd/system/webhook.service`
* `systemctl start webhook`
* `systemctl status webhook`
* `journalctl -f -u webhook.service` - follow service logs
* `crontab -e`

## Monitoring

* `docker logs -f --tail 10 albums_listener_1` - view container logs
* `sudo grep CRON /var/log/syslog` - view cron logs
