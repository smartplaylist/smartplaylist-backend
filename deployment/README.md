# Installation

* `sudo apt-get install webhook`
* `cat webhook.service > /lib/systemd/system/webhook.service`
* `systemctl start webhook`
* `systemctl status webhook`
* `journalctl -u webhook.service` Check logs
