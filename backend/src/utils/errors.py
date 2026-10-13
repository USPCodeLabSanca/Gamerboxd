
# Mensagens muito utilizadas
LIST_NOT_FOUND_MSG = "Lista não encontrada!"
PRIVATE_LIST_MSG = "Essa lista é privada!"
LACK_OF_LIST_OWNERSHIP_MSG = "Apenas o autor da lista pode realizar esta ação!"
BLOCKED_BY_LIST_OWNER = "O usuário está bloqueado pelo autor da lista!"


class QueryError(Exception):
    """Erro genérico"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

