from functools import wraps

from gdo.base.Application import Application
from gdo.base.Exceptions import GDOError
from gdo.date.Time import Time


def WithRateLimit(func=None, max_calls: int = 6, within: float = 60.0):
    """
    Rate Limit decorator for Method.gdo_execute() call.
    You can overload gdo_rate_limit_calls() and gdo_rate_limit_timeout() (getters) OR
    use decorator parameters "max_calls" and "within".
    v8.01
    (c) 2024 Chappy and gizmore
    """
    if func is None:
        return lambda f: WithRateLimit(f, max_calls, within)

    # Define a function to read parameters from the database
    def get_rate_limit_parameters(self=None):
        nonlocal max_calls, within
        try:
            max_calls = self.gdo_rate_limit_calls()
        except Exception as ex:
            pass
        try:
            within = self.gdo_rate_limit_timeout()
        except Exception as ex:
            pass
        return max_calls, within

    def decorator(func):

        calls_made = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal calls_made, max_calls, within
            t = Application.TIME
            cut = t - within
            calls_made[:] = [call_time for call_time in calls_made if call_time > cut]
            if len(calls_made) >= max_calls:
                min_wait_time = within - (t - calls_made[0])
                raise GDOError('err_rate_limit_exceeded', [max_calls, Time.human_duration(within), Time.human_duration(min_wait_time)])

            calls_made.append(t)
            return func(*args, **kwargs)

        return wrapper

    if hasattr(func, "__self__") and func.__self__ is not None:
        max_calls, within = get_rate_limit_parameters(func.__self__)

    return decorator(func)
