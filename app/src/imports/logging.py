import logging
import os

import structlog

logging.basicConfig(level=os.environ.get("GRABBER_LOGLEVEL", "WARN"))
logging.getLogger("spotipy").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)


def get_logger(name):
    log = structlog.get_logger(name)
    log = log.bind(logger=name)
    return log


# loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
# for logger in loggers:
#     logger.setLevel(logging.INFO)

# print(f"logs: {loggers}")
