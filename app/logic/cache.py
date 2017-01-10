from django.core.cache import cache


def cached(key_func):
    """
    Decorator that creates cached versions of expensive functions.
    """
    def decorator(func):
        def decorated(*args, **kwargs):
            key = key_func(*args, **kwargs)
            return cache.get_or_set(key, lambda: func(*args, **kwargs))
        return decorated
    return decorator
