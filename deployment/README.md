# Production deployment

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

### Run www

* `docker run -d --rm --network my-bridge-network --env-file .env --hostname gt_www -p 3001:3001 --name www jkulak/grabtrack-www:latest`

### Run listeners

* `docker run -d --rm --network my-bridge-network --env-file .env app pipenv run python get_albums.py`

## Monitoring

* `docker logs -f --tail 10 albums_listener_1` - view container logs
* `sudo grep CRON /var/log/syslog` - view cron logs

## Cron

* `crontab -e`
* `crontab -l`

```cron
25 12 * * * /home/www/deployment/run_spotify_update.sh >> /home/www/cron_results
10 23 * * * /home/www/db_backup/db_backup.sh >> /home/www/db_backup/cron_db_backup_results
```

## Webhooks

### Installation

We need `webhook` at least 2.8.0 version which is not available through `apt-get`.
I had problems installing it with `snap`.
Solution: install older version using `apt-get` and overwrite the binary file (built from GitHub).

* `sudo apt-get install webhook`
* Install Go (<https://go.dev/doc/install>)
* Clone `https://github.com/adnanh/webhook` repository
* `go build github.com/adnanh/webhook`
* `sudo ln -s /home/www/webhook/webhook /usr/bin/webhook`
* Test `which webhook` and `webhook --version`
* Edit `/lib/systemd/system/webhook.service` (change `ExecStart=/usr/bin/webhook -nopanic -verbose -hotreload -hooks /home/www/deployment/hooks.json`)

### Service management and monitoring

* `systemctl start webhook`
* `systemctl status webhook`
* `journalctl -f -u webhook.service` - follow service logs
