import logging
import os

import structlog

log_level = os.environ.get("GRABBER_LOGLEVEL", "WARN")
logging.basicConfig(level=log_level)
logging.getLogger("spotipy").setLevel(log_level)
logging.getLogger("urllib3").setLevel(log_level)


def get_logger(name):
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    )

    log = structlog.get_logger(name)
    log = log.bind(logger=name)
    return log


# loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
# for logger in loggers:
#     logger.setLevel(logging.INFO)

# print(f"logs: {loggers}")
