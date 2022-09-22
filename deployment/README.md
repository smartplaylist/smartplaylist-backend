# Installation

* `sudo apt-get install webhook`
* `cat webhook.service > /lib/systemd/system/webhook.service`
* `systemctl start webhook`
* `systemctl status webhook`
* `journalctl -f -u webhook.service` - follow service logs
* `crontab -e`

## Monitoring

* `docker logs -f --tail 10 albums_listener_1` - view container logs
* `sudo grep CRON /var/log/syslog` - view cron logs
