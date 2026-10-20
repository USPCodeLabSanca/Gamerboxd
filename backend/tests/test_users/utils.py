from math import ceil
from ..utils import *


SUCCESS_CREATING_MSG = {"message": "Conta criada com sucesso!", "id": "abc"}

SUCCESS_FOLLOWING_MSG = {"message":"Conta seguida com sucesso!"}
SUCCESS_UNFOLLOWING_MSG = {"message":"Conta desseguida com sucesso!"}
CANT_FOLLOW_YOURSELF_MSG = {"message":"O usuário não pode seguir a si mesmo!"}
FOLLOW_SOMEONE_WHO_BLOCKED_YOU_MSG = {"message":"O usuário está tentando seguir alguém que o bloqueou!"}
FOLLOW_SOMEONE_WHO_YOUVE_BLOCKED_MSG = {"message": "Não é possível ver detalhes de um usuário antes de desbloqueá-lo!"}

SUCCESS_BLOCKING_MSG = {"message":"Conta bloqueada com sucesso!"}
SUCCESS_UNBLOCKING_MSG = {"message":"Conta desbloqueada com sucesso!"}
CANT_BLOCK_YOURSELF_MSG = {"message":"O usuário não pode bloquear a si mesmo!"}

USER_NOT_FOUND_MSG = {"message":"Usuário não encontrado!"}

USERNAME_WRONG_LENGTH_MSG = {"message": "O username deve ter entre 4 e 24 caracteres!"}
USERNAME_IN_USE_MSG = lambda username: {"message": f'O username "{username}" já está sendo utilizado!'}

INVALID_EMAIL_MSG = {"message": "Email inválido!"}
EMAIL_IN_USE_MSG = lambda email: {"message": f'O email "{email}" já está sendo utilizado!'}

PWD_WRONG_LENGTH_MSG = {"message": "A senha deve conter entre 8 a 64 caractéres!"}
PWD_WITHOUT_NUM_MSG = {"message": "A senha deve conter pelo menos um número!"}
PWD_WITHOUT_SYMB_MSG = {"message": "A senha deve conter pelo menos um símbolo!"}
PWD_WITHOU_CAP_MSG = {"message": "A senha deve conter pelo menos uma letra minúscula e uma letra maiúscula!"}

BIO_WRONG_LENGTH_MSG = {"message": "A bio não pode ter mais que 280 caractéres!"}
EMPTY_BIO_MSG = {"message": "A bio não pode ser apenas espaço vazio!"}

