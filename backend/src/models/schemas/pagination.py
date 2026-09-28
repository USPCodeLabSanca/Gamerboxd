from pydantic import BaseModel
from fastapi import Query

class PageResult(BaseModel):
    """Modelo para retorno de paginação"""

    page_size: int = 10
    previous: str = None
    current: str
    next: str = None
    content: list


class PageQuery(BaseModel):
    """Modelo para recebimento de paginação"""

    page_size: int = Query(default=10) 
    cursor: str = Query()
