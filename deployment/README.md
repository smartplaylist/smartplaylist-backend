# Installation

* `sudo apt-get install webhook`
* `cat webhook.service > /lib/systemd/system/webhook.service`
* `systemctl start webhook`
* `systemctl status webhook`
* `journalctl -f -u webhook.service` Follow service logs
