import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/review"

SUCCESS_CREATING_MSG = {"message":"Review criada com sucesso!"}
SUCCESS_DELETING_MSG = {"message":"Review deletada com sucesso!"}
SUCCESS_LIKING_MSG = {"message": "Like adicionado com sucesso!"}
SUCCEESS_UNLIKING_MSG = {"message": "Like removido com sucesso!"}
REVIEW_NOT_FOUND_MSG = {"message": "Review não encontrada!"}
USER_NOT_FOUND_MSG = {"message":"Usuário não encontrado!"}