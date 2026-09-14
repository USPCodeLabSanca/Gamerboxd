import pytest
import requests

BASE_URL = "http://127.0.0.1:8000/user"

SUCCESS_CREATING_MSG = {"message": "Conta criada com sucesso!"}
SUCCESS_FOLOWING_MSG = {"message":"Conta seguida com sucesso!"}
SUCCESS_UNFOLOWING_MSG = {"message":"Conta desseguida com sucesso!"}
SUCCESS_BLOCKING_MSG = {"message":"Conta bloqueada com sucesso!"}
SUCCESS_UNBLOCKING_MSG = {"message":"Conta desbloqueada com sucesso!"}
USER_NOT_FOUND_MSG = {"message":"Usuário não encontrado!"}