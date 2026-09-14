from . import *


new_lists = [
    # Testes funcionais
    (
        {"name": "list_1", "description": "list_1", "is_private": True},
        200,  SUCCESS_CREATING_MSG 
    ),

    (
        {"name": "list_2", "description": "list_2"},
        200,  SUCCESS_CREATING_MSG
    ),

    (
        {"name": "list_3", "is_private": False},
        200,  SUCCESS_CREATING_MSG
    ),

    (
        {"name": "list_4",},
        200,  SUCCESS_CREATING_MSG
    ),

    # Testes de erros do usuário na hora de criar conta
    (
        {"name": "list_1", "description": "list_5"},
        409,  {"message": 'O usuário já possui uma lista com o nome "list_1"!'}
    ),

    (
        {"name": "list_6" * 10},
        400,  {"message": "O nome da lista não pode exceder 45 caractéres!"}
    ),

    (
        {"name": "         ", "description": "list_7 "},
        400,  {"message": "O nome da lista não pode ser apenas espaço vazio!"}
    ),

    (
        {"name": "list_8", "description": "list_8 " * 55},
        400,  {"message": "A descrição da lista não pode exceder 300 caractéres!"}
    ),

    (
        {"name": "list_9", "description": "         "},
        400,  {"message": "A descrição da lista não pode ser apenas espaço vazio!"}
    ),

    # Testes de schema inválido/mal formatado
    ({"name": 110}, 422, None),
    ({"name": None, "description": "list_11"}, 422, None),
    ({"list_name": "list_12"}, 422, None),
    ({"name": "list_13", "description": 112}, 422, None),
    ({"name": "list_14", "is_private": 113}, 422, None),
    ({"name": "list_15", "is_private": None}, 422, None),
    
]


@pytest.mark.parametrize("list_in,expected_status,expected_body", new_lists)
def test_new_lists(users, list_in, expected_status, expected_body):

    user = users["Alice"].copy()
    cookies = user.pop("cookies")

    if ("description" in list_in) and (list_in["description"] == "list_5"):
        list1 = {"name": "list_1", "description": "list_1", "is_private": True}
        response_duplicate = requests.post(url=BASE_URL, json=list1, cookies=cookies)
        assert response_duplicate.status_code == 200

    response = requests.post(url=BASE_URL, json=list_in, cookies=cookies)
    assert response.status_code == expected_status

    if expected_body is not None:
        assert response.json() == expected_body

    if response.status_code == 200:
        response_delete = requests.delete(url=BASE_URL + f"/{list_in["name"]}", cookies=cookies)
        assert response_delete.status_code == 200

    if ("description" in list_in) and (list_in["description"] == "list_5"):
        response_delete_duplicate = requests.delete(url=BASE_URL + f"/{list1["name"]}", cookies=cookies)
        assert response_delete_duplicate.status_code == 200
