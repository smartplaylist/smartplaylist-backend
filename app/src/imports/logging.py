import logging
import os

import structlog

log_level = os.environ.get("GRABBER_LOGLEVEL", "WARNING")
logging.basicConfig(level=log_level)
logging.getLogger("spotipy").setLevel("WARNING")
logging.getLogger("urllib3").setLevel(log_level)
logging.getLogger("requests").setLevel(log_level)
logging.getLogger("pika").setLevel("WARNING")


def get_logger(name):
    structlog.configure(
        # processors=[
        #     structlog.processors.add_log_level,
        #     structlog.processors.TimeStamper(fmt="iso", key="ts"),
        #     structlog.processors.JSONRenderer(),
        # ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level)
        ),
    )

    log = structlog.get_logger(name)
    log = log.bind(logger=name)
    return log
