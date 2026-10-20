
# Mensagens muito utilizadas
LIST_NOT_FOUND_MSG = "Lista não encontrada!"
PRIVATE_LIST_MSG = "Essa lista é privada!"
LACK_OF_LIST_OWNERSHIP_MSG = "Apenas o autor da lista pode realizar esta ação!"
BLOCKED_BY_LIST_OWNER_MSG = "O usuário está bloqueado pelo autor da lista!"
USER_BLOCKED_LIST_OWNER_MSG = "Não é possível ver detalhes da lista um usuário antes de desbloqueá-lo!"

REVIEW_NOT_FOUND_MSG = "Review não encontrada!"
PRIVATE_REVIEW_MSG = "Essa review é privada!"
LACK_OF_REVIEW_OWNERSHIP_MSG = "Apenas o autor da review pode realizar essa ação!"
BLOCKED_BY_REVIEW_OWNER_MSG = "O usuário está bloqueado pelo autor da review!"
USER_BLOCKED_REVIEW_OWNER_MSG = "Não é possível ver detalhes da review um usuário antes de desbloqueá-lo!"

USER_NOT_FOUND_MSG = "Usuário não encontrado!"
BLOCKED_BY_USER_MSG = "O usuário está tentando ver detalhes da conta de alguém que o bloqueou!"
USER_BLOCKED_OTHER_MSG = "Não é possível ver detalhes de um usuário antes de desbloqueá-lo!"
LACK_OF_USER_PERMISSION_MSG = "O usuário não tem permissão para ver estes detalhes!"

class QueryError(Exception):
    """Erro genérico"""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

