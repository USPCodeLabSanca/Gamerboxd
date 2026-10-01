
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


class AuthError(QueryError):
    """Erro de autenticação. Era para o usuário estar autenticado para acessar essa funcionalidade"""
    def __init__(self, message: str):
        super().__init__(401, message)


class UserError(QueryError):
    """Erro no input do usuário"""
    def __init__(self, message: str):
        super().__init__(400, message)


class ForbidenError(QueryError):
    """Erro de permissão. O usuário não deveria ter conseguido acessar essa funcionalidade"""
    def __init__(self, message: str):
        super().__init__(403, message)


class NotFoundError(QueryError):
    """Erro de objeto não encontrado/existente"""
    def __init__(self, message: str):
        super().__init__(404, message)


class RequestError(QueryError):
    """Erro na hora de chamar uma rota"""
    def __init__(self, message: str):
        super().__init__(406, message)


class ConflictError(QueryError):
    """Erro de duplicidade. Alguma informação do input viola a unicidade de uma coluna do DB"""
    def __init__(self, message: str):
        super().__init__(409, message)