import time
from functools import wraps
from utils.logger import logger

def retry_with_backoff(retries=3, backoff_in_seconds=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        logger.error(f"Function {func.__name__} failed after {retries} retries: {e}")
                        raise
                    
                    sleep = (backoff_in_seconds * (2 ** x))
                    logger.warning(f"Retrying {func.__name__} in {sleep}s due to: {e}")
                    time.sleep(sleep)
                    x += 1
        return wrapper
    return decorator
