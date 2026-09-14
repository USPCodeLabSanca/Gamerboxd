import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/list"

SUCCESS_CREATING_MSG = {"message":"Lista criada com sucesso!"}
SUCCESS_DELETING_MSG = {"message":"Lista deletada com sucesso!"}
SUCCESS_SAVING_MSG = {"message": "Lista salva com sucesso!"}
SUCCEESS_UNSAVING_MSG = {"message": "Lista dessalvada com sucesso"}
SUCCESS_ADDING_MSG = {"message": "Jogo adicionado à lista com sucesso"}
SUCCEESS_REMOVING_MSG = {"message": "Jogo removido da lista com sucesso"}
LIST_NOT_FOUND_MSG = {"message": "Lista não encontrada!"}
USER_NOT_FOUND_MSG = {"message":"Usuário não encontrado!"}