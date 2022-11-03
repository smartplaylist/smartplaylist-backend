import os

from imports.logging import get_logger
from spotipy.exceptions import SpotifyException

MAX_RETRY_ATTEMPTS = 10

log = get_logger(os.path.basename(__file__))


def api_attempts(func, *args, **kwargs):
    def inner_function(*args, **kwargs):
        attempt = 0
        while attempt < MAX_RETRY_ATTEMPTS:
            try:
                func(*args, **kwargs)
                print(args)
                print(kwargs)
                log.info(
                    "Trying API request",
                    attempt=attempt,
                    spotify_id=kwargs["id"],
                    object=kwargs["object_type"],
                )
                break
            except SpotifyException as e:
                attempt += 1
                log.exception(
                    "Spotipy Exception",
                    msg=repr(e),
                    attempt=attempt,
                    spotify_id=kwargs["id"],
                    object=kwargs["object_type"],
                    exc_info=False,
                )
            except Exception as e:
                attempt += 1
                log.exception(
                    "Unhandled exception",
                    exception=e,
                    attempt=attempt,
                    spotify_id=kwargs["id"],
                    object=kwargs["object_type"],
                    exc_info=True,
                )

    return inner_function
