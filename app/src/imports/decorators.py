import functools

from imports.logging import get_logger
from spotipy.exceptions import SpotifyException


def normalize_arg(data):
    return data if len(data) > 21 else data["href"]


def api_attempts(_func=None, *, num_times=5):
    log = get_logger("api_attempts")

    def decorator_repeat(func):
        @functools.wraps(func)
        def inner_function(*args):
            result = {}
            for i in range(1, num_times + 1):
                try:
                    result = func(*args)
                except SpotifyException as e:
                    log.exception(
                        "Spotipy Exception",
                        msg=repr(e),
                        attempt=i,
                        arg0=normalize_arg(args[0]),
                        function=func.__name__,
                        exc_info=False,
                    )
                except Exception as e:
                    log.exception(
                        "Unhandled exception",
                        exception=e,
                        attempt=i,
                        arg0=normalize_arg(args[0]),
                        function=func.__name__,
                        exc_info=True,
                    )
                else:
                    log.info(
                        "⚡️ Trying API request",
                        attempt=i,
                        arg0=normalize_arg(args[0]),
                        function=func.__name__,
                    )
                    return result
            return result

        return inner_function

    if _func is None:
        return decorator_repeat
    else:
        return decorator_repeat(_func)
