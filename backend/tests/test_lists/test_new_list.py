from .utils import *

def base_list(num:int, **overrides):
    """Payload padrão de uma lista"""

    list_in = {"name": f"list_{num}"}

    list_in.update(overrides)
    return list_in


new_lists = [
    # Testes funcionais
    (base_list(1, description="list1", is_private=True), 200,  SUCCESS_CREATING_MSG),
    (base_list(2, description="list2"), 200,  SUCCESS_CREATING_MSG),
    (base_list(3, is_private=True), 200,  SUCCESS_CREATING_MSG),
    (base_list(4), 200, SUCCESS_CREATING_MSG),

    # Testes de erros do usuário na hora de criar conta
    (base_list(1), 409, {"message": 'O usuário já possui uma lista com o nome "list_1"!'}),
    (base_list(6, name="list6"*10), 400, {"message": "O nome da lista não pode exceder 45 caractéres!"}),
    (base_list(7, name="  "), 400, {"message": "O nome da lista não pode ser apenas espaço vazio!"}),
    (base_list(8, description="list8"*61), 400,  {"message": "A descrição da lista não pode exceder 300 caractéres!"}),
    (base_list(7, description="  "), 400,  {"message": "A descrição da lista não pode ser apenas espaço vazio!"}),

    # Testes de schema inválido/mal formatado
    (base_list(8, name=8), 422, None),
    (base_list(9, name=None), 422, None),
    ({"list_name": "list_10"}, 422, None),
    (base_list(11, description=11), 422, None),
    (base_list(12, is_private=12), 422, None),
    (base_list(13, is_private=None), 422, None),
    
]


@pytest.mark.parametrize("list_in,expected_status,expected_body", new_lists)
def test_new_lists(users, list_in, expected_status, expected_body):

    user = users["Alice"].copy()
    cookies = user.pop("cookies")

    # Força a duplicidade para testes de conflito
    if expected_status == 409:
        list1 = base_list(1)
        response_duplicate = requests.post(url=BASE_URL, json=list1, cookies=cookies)
        assert response_duplicate.status_code == 200
        duplicate_list_id = response_duplicate.json()["id"]

    response = requests.post(url=BASE_URL, json=list_in, cookies=cookies)
    assert response.status_code == expected_status

    if expected_body is not None:
        assert expected_body.keys() == response.json().keys()
        assert expected_body["message"] == response.json()["message"]

        list_id = response.json()["id"] if expected_status == 200 else None

    if response.status_code == 200:
        response_delete = requests.delete(url=BASE_URL + f"/{list_id}", cookies=cookies)
        assert response_delete.status_code == 200

    if expected_status == 409:
        response_delete_duplicate = requests.delete(url=BASE_URL + f"/{duplicate_list_id}", cookies=cookies)
        assert response_delete_duplicate.status_code == 200



def test_created_lists_page_has_all_fields(users):
    """Verifica se as páginas tem os campos corretos, mesmo sem que haja listas para o usuário"""

    user1 = users["Alice"]

    # Campos de uma pagina de resultados
    page_fields = ("total", "page_size", "previous_page", "current_page", "next_page", "content")

    # Pega uma página de bloqueados pelo user1
    response = requests.get(BASE_URL + f"/created/{user1["user_id"]}", cookies=user1["cookies"])
    assert response.status_code == 200, response.json()
    page = response.json()

    # Verifica que a página tem todos os dados
    for pf in page_fields:
        assert pf in page.keys(), pf


def test_created_lists_page_has_all_fields_after_list_creation(users):
    """Verifica se as páginas tem os campos corretos"""

    user1 = users["Alice"]

    list_in = create_list(user1)

    # Campos de uma pagina de resultados
    page_fields = ("total", "page_size", "previous_page", "current_page", "next_page", "content")

    # Pega uma página de listas criadas pelo user1
    response = requests.get(BASE_URL + f"/created/{user1["user_id"]}", cookies=user1["cookies"])
    assert response.status_code == 200, response.json()
    page = response.json()

    # Verifica que a página tem todos os dados
    for pf in page_fields:
        assert pf in page.keys(), pf

    # Campos do conteúdo de uma página
    content_fields = ("name", "list_id", "creator", "list_saves_count")
    creator_fields = ("user_id", "username", "pfp")

    content = page["content"]

    # Verifica que o conteúdo da página tem todos os dados
    for cf in content_fields:
        assert cf in content[0].keys(), cf

        if cf == "creator":
            for crf in creator_fields:
                assert crf in content[0][cf].keys(), crf

    delete_list(user1, list_in)
