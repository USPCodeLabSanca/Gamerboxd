from functools import wraps
from .errors import QueryError

def db_query(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except Exception as e:
            raise QueryError(500, f"{func.__name__}: {e}")
    
    return wrapper




