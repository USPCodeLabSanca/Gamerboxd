from . import BASE_URL, pytest, requests
    
new_users = [
    # Teste funcional
    (
        {"username": "user1", "password": "UserUser1!", "email": "user1@gmail.com"},
        200, {"message": "Conta criada com sucesso!"}
    ),

    # Testes de erros do usuário na hora de criar conta
    (
        {"username": "u2", "password": "UserUser2!", "email": "user2@gmail.com"},
        400, {"message": "O username deve ter entre 4 e 24 caracteres!"}
    ),

    (
        {"username": "user3" * 6, "password": "UserUser3!", "email": "user3@gmail.com"},
        400, {"message": "O username deve ter entre 4 e 24 caracteres!"}
    ),

    (
        {"username": "user1", "password": "UserUser4!", "email": "user4@gmail.com"},
        409, {"message": 'O username "user1" já está sendo utilizado!'}
    ),

    (
        {"username": "user5", "password": "UserUser5!", "email": "user5"},
        400, {"message": "Email inválido!"}
    ),

    (
        {"username": "user6", "password": "UserUser6!", "email": "user1@gmail.com"},
        409, {"message": 'O email "user1@gmail.com" já está sendo utilizado!'}
    ),

    (
        {"username": "user7", "password": "User7!", "email": "user7@gmail.com"},
        400, {"message": "A senha deve conter entre 8 a 64 caractéres!"}
    ),

    (
        {"username": "user8", "password": "User8!" * 11 , "email": "user8@gmail.com"},
        400, {"message": "A senha deve conter entre 8 a 64 caractéres!"}
    ),

    (
        {"username": "user9", "password": "UserUser!" , "email": "user9@gmail.com"},
        400, {"message": "A senha deve conter pelo menos um número!"}
    ),

    (
        {"username": "user10", "password": "UserUser10" , "email": "user10@gmail.com"},
        400, {"message": "A senha deve conter pelo menos um símbolo!"}
    ),

    (
        {"username": "user11", "password": "useruser11!" , "email": "user11@gmail.com"},
        400, {"message": "A senha deve conter pelo menos uma letra minúscula e uma letra maiúscula!"}
    ),

    (
        {"username": "user12", "password": "USERUSAER12!" , "email": "user12@gmail.com"},
        400, {"message": "A senha deve conter pelo menos uma letra minúscula e uma letra maiúscula!"}
    ),

    # Testes de schema inválido/mal formatado
    ({"username": 13, "password": "UserUser13!", "email": "user13@gmail.com"}, 422, None),
    ({"user": "user14", "password": "UserUser14!", "email": "user14@gmail.com"}, 422, None),
    ({"username": "user15", "password": 15, "email": "user15@gmail.com"}, 422, None),
    ({"username": "user16", "pwd": "UserUser16!", "email": "user16@gmail.com"}, 422, None),
    ({"username": "user17", "password": "UserUser17!", "email": 17}, 422, None),
    ({"username": "user18", "password": "UserUser18!",  "gmail": "user18@gmail.com"}, 422, None),
    ({"username": None, "password": "UserUser19!", "email": "user19@gmail.com"}, 422, None),
    ({"username": "user20", "password": None, "email": "user20@gmail.com"}, 422, None),
    ({"username": "user21", "password": "UserUser21!", "email": None}, 422, None),
    ({"password": "UserUser22!", "email": "user22@gmail.com"}, 422, None),
    ({"username": "user23", "email": "user23@gmail.com"}, 422, None),
    ({"username": "user24", "password": "UserUser24!"}, 422, None)
]


@pytest.mark.parametrize("user,expected_status,expected_body", new_users)
def test_new_users(user, expected_status, expected_body):
    response = requests.post(url=BASE_URL + "/user", json=user)

    assert response.status_code == expected_status
    assert response.cookies is not None

    if expected_body is not None:
        assert response.json() == expected_body

