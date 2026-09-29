class QueryError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


class NotFoundError(QueryError):
    def __init__(self, message: str):
        super.__init__(404, message)