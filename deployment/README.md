# Production deployment

## Production location and access

| What | Where |
|------|--------|
| **Public site** | **https://smartplaylist.me** (see `docs/dev_blog.md`, CORS in `api/src/lib/server.py`) |
| **API** | Exposed via reverse proxy at https://smartplaylist.me/fastapi/ (backend container `fastapi` on port 8008; proxy config in [smartplaylist-reverseproxy](https://github.com/jkulak/smartplaylist-reverseproxy)) |
| **Server hostname** | **`rapid`** — `188.68.231.182`. SSH: `ssh www@rapid`. To discover the IP: `dig smartplaylist.me` or `nslookup smartplaylist.me` — it resolves to `188.68.231.182`. Add to `/etc/hosts` if needed: `188.68.231.182  rapid`. See `_DEV/restore_newest_backup.sh` for `scp` usage. |
| **Paths on server** | `/home/www/deployment` (scripts, `hooks.json`), `/home/www/spotify-grabtrack` (`.env`), `/home/www/smartplaylist_api` (API deploy dir), `/home/www/db_backup` (DB backups). User `www`. |
| **Deploy** | Push tag `api-vX.Y.Z` or `app-vX.Y.Z` → workflow builds image → calls webhook `DEPLOY_WEBHOOK_URL/deploy-api` or `.../deploy-app` with `WEBHOOK_SECRET`. |

**Check if production is up (from your machine):**

```bash
# Site and API (nginx routes /fastapi/ to the API container)
curl -sI https://smartplaylist.me
curl -s https://smartplaylist.me/fastapi/init
```

**SSH to production:** `ssh www@rapid`. Then:

```bash
# API container
docker ps | grep fastapi
docker logs -f --tail 50 fastapi

# Listeners
docker logs -f --tail 10 albums_listener_1
```

---

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
* Run `./deployment/first_deployment.sh`

### Prepare new database

* `docker build -t alembic-image ./db`
* `docker run -ti -v $(pwd)/db:/db --rm --network smartplaylist_network alembic-image alembic upgrade head`

### Import followed artists

* `docker build -t app ./app`
* `docker run -ti --rm --network smartplaylist_network -p 8083:8083 -v $(pwd)/app/src:/app --env-file .env app pipenv run python sync_followed_artists.py`

### Run www

* <https://github.com/jkulak/smartplaylist-www/tree/main/deployment>

### Run listeners

* Run the app deployment script `./deployment/deploy_app.sh`

## Monitoring

* `docker logs -f --tail 10 albums_listener_1` - view container logs
* `sudo grep CRON /var/log/syslog` - view cron logs

## Cron


* `crontab -e`
* `crontab -l`

Contab configuration in `deployment/cron_scripts/crontab`.

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
