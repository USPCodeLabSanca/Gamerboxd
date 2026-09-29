from pydantic import BaseModel
from fastapi import Query

class PageResult(BaseModel):
    """Dados de uma página"""

    total: int
    page_size: int = 10
    previous_page: str | None = None
    current: str | None = None
    next_page: str | None = None
    content: list


class PageQuery(BaseModel):
    """Dados necessários para estabelecer paginação"""

    page_size: int = Query(default=10) 
    cursor: str | None = Query(default=None)
    search: str | None = Query(default=None)

def convert_cursors_to_paths(page_result: PageResult, current_path: str) -> PageResult:
    """Converte os cursores de encoded strs para paths de rota que o frontend pode acessar mais facilmente"""

    start_index = current_path.find("cursor=")

    # Primeira busca (cursor não existe, então só colocar no final)
    if start_index == -1:
        query_char = "&" if "?" in current_path else "?"
        prev_path = None
        next_path = current_path + query_char + "cursor=" + page_result.next_page if page_result.next_page is not None else None

    # Outra busca já usando o cursor de uma busca passada
    else:
        start_index += len("cursor=")

        # Acha o que tiver depois do query parameter "cursor"
        end_index = current_path[start_index:].find("&")

        start_of_path = current_path[:start_index]
        end_of_path = current_path[start_index + end_index:] if end_index != -1 else ""

        next_path = start_of_path + page_result.next_page + end_of_path if page_result.next_page is not None else None

        # Página > 2
        if page_result.previous_page is not None:
            prev_path = start_of_path + page_result.previous_page + end_of_path

        # Página 2
        else:
            before = start_of_path[:-1*len("cursor=")]   

            # Se existia outro query parameter depois do cursor, só remove o "&cursor=abc" de dentro da string
            if len(end_of_path) != 0:
                prev_path = before + end_of_path[1:]

            # Se não existia outro query parameter depois do cursor, só tira o ? ou &
            else:
                prev_path = before.rstrip("?&")

    page_result.current = current_path
    page_result.previous_page = prev_path
    page_result.next_page = next_path

    return page_result