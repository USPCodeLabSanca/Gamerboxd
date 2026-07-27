from functools import wraps

class QueryError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def db_query(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(args, kwargs)

        except Exception as e:
            raise QueryError(500, str(e))
    
    return wrapper
