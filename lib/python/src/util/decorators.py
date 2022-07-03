from functools import wraps
from cattrs import structure


def structure_input(event_class):
    def outer(f):
        @wraps(f)
        def wrapper(event, ctx):
            input_event = structure(event, event_class)
            return f(input_event, ctx)

        return wrapper

    return outer
