from .utils import *

def base_user(num:int, **overrides):
    """Payload padrão de um usuário"""

    user = {
        "username": f"user{num}",
        "password": f"UserUser{num}!",
        "email": f"user{num}@gmail.com"
    }

    user.update(overrides)
    return user


new_users = [
    # Teste funcional
    (base_user(1), 200, SUCCESS_CREATING_STR),

    # Testes de erros do usuário na hora de criar conta
    (base_user(2, username = "u2"), 400, USERNAME_WRONG_LENGTH_MSG),        # username muito curto
    (base_user(3, username = "user3"*20), 400, USERNAME_WRONG_LENGTH_MSG),  # username muito longo
    (base_user(4, username = "user1"), 409, USERNAME_IN_USE_MSG("user1")),  # username já está em uso

    (base_user(5, email = "user5"), 400, INVALID_EMAIL_MSG),                                # email inválido
    (base_user(6, email = "user1@gmail.com"), 409, EMAIL_IN_USE_MSG("user1@gmail.com")),    # email já em uso

    (base_user(7, password = "User7!"), 400, PWD_WRONG_LENGTH_MSG),         # senha muito curta
    (base_user(8, password = "User8!" * 11), 400, PWD_WRONG_LENGTH_MSG),    # senha muito longa
    (base_user(9, password ="UserUser!"), 400, PWD_WITHOUT_NUM_MSG),        # senha não tem digito
    (base_user(10, password = "UserUser10"), 400, PWD_WITHOUT_SYMB_MSG),    # senha não tem símbolo
    (base_user(11, password = "useruser11!"), 400, PWD_WITHOU_CAP_MSG),     # senha não tem letra maiuscula
    (base_user(12, password = "USERUSAER12!"), 400, PWD_WITHOU_CAP_MSG),    # senha não tem letra minuscula

    # Testes de schema inválido/mal formatado - tipos errados
    (base_user(13, username = 13), 422, None),
    (base_user(14, username = None), 422, None),
    (base_user(15, email = 17), 422, None),
    (base_user(16, email = None), 422, None),
    (base_user(17, password = 15), 422, None),
    (base_user(18, password = None), 422, None),

    # Testes de schema inválido/mal formatado - campo faltando
    ({k: v for k, v in base_user(19).items() if k != "username"}, 422, None),
    ({k: v for k, v in base_user(20).items() if k != "email"}, 422, None),
    ({k: v for k, v in base_user(21).items() if k != "password"}, 422, None),

    # Vazio
    ({}, 422, None)
]


@pytest.mark.parametrize("user,expected_status,expected_body", new_users)
def test_new_users(user, expected_status, expected_body):

    # Força a duplicidade para testes de conflito
    if expected_status == 409:
        response_duplicate = requests.post(url=BASE_URL, json=base_user(1))
        assert response_duplicate.status_code == 200
        assert response_duplicate.cookies is not None
        for c in response_duplicate.cookies:
            c.secure = False

    response = requests.post(url=BASE_URL, json=user)

    assert response.status_code == expected_status, response.json()
    assert response.cookies is not None

    response_json = response.json()
    if expected_body is not None:
        if type(expected_body) == str:
            assert "message" in response.json().keys()
            assert response_json["message"] == expected_body

        else:
            assert response_json == expected_body

    # Limpa a conta do DB caso a sua inserção tenha dado certo
    if response.status_code == 200:
        assert "id" in response_json.keys()
        
        for c in response.cookies:
            c.secure = False
        response_delete = requests.delete(BASE_URL, cookies=response.cookies)
        assert response_delete.status_code == 200

    # Se era teste de conflito, remove o duplicado do DB
    if expected_status == 409:
        response_delete_duplicate = requests.delete(BASE_URL, cookies=response_duplicate.cookies)
        assert response_delete_duplicate.status_code == 200

