from functools import wraps
from models.schemas.pagination import PageResult, PageQuery

class QueryError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def db_query(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except Exception as e:
            raise QueryError(500, f"{func.__name__}: {e}")
    
    return wrapper


def paginate_result(page_result: PageResult, page_query: PageQuery):

    page_result.page_size = page_query.page_size
    cursor_str = "cursor="
    start_index = page_result.current.find(cursor_str) + len(cursor_str)
    if start_index == -1:
        raise QueryError(500, "cursor já era pra estar no page_result!")

    end_index = page_result.current[start_index:].find("&")
    start_of_str = page_result.current[:start_index]
    end_of_str = page_result.current[end_index:]
    if page_result.next != None:
        page_result.next = start_of_str + page_result.next + end_of_str

    if page_result.previous is not None:
        page_result.previous = start_of_str + page_result.previous + end_of_str

    return page_result


