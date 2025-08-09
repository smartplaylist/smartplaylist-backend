import functools

from imports.logging import get_logger

log = get_logger("handle_exceptions")


def handle_exceptions(_func=None):
    def decorator(func):
        @functools.wraps(func)
        def inner_function(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log.exception(
                    "Unhandled exception",
                    exception=e,
                    function=func.__name__,
                    exc_info=True,
                )
                return None

        return inner_function

    if _func is None:
        return decorator
    else:
        return decorator(_func)
