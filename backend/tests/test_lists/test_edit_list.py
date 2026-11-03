from .utils import *


def test_edit_list_name_to_not_used_one_200(users, create_list, edit_list_request):
    """Alice cria uma lista e troca o seu nome para um nome não utilizado"""

    user = users["Alice"]
    list_edit = create_list(user)
    list_edit.name = "Nova Lista da Alice"
    
    response = edit_list_request(user, list_edit)
    assert response.status_code == 200, response.json()
    assert response.json()["name"] == list_edit.name


def test_edit_list_name_to_used_one_returns_409(users, create_list, edit_list_request):
    """Alice cria duas listas e tenta renomear a segunda para o nome da primeira"""

    user = users["Alice"]
    list1 = create_list(user)
    list2 = create_list(user, list_name="Segunda Lista")
    list2.name = list1.name

    response = edit_list_request(user, list2)
    assert response.status_code == 409, response.json()
    assert response.json() == LIST_NAME_TAKEN(list1.name)


def test_edit_list_description_returns_200(users, create_list, edit_list_request):
    """Alice cria uma lista e adiciona uma descrição a ela"""

    user = users["Alice"]
    list_edit_description = create_list(user)
    list_edit_description.description = "Minha lista favorita de jogos"

    response = edit_list_request(user, list_edit_description)
    assert response.status_code == 200, response.json()
    assert response.json()["description"] == list_edit_description.description


def test_edit_list_description_out_of_bounds_returns_400(users, create_list, edit_list_request):
    """Alice tenta colocar uma descrição muito grande na sua lista, e depois uma descrição vazia"""

    user = users["Alice"]
    list_edit_description_out_of_bounds = create_list(user, privacy=Clearence.OWNER)
    list_edit_description_out_of_bounds.description = user.username * 100
    list_edit_description_out_of_bounds.privacy = Clearence.ANY

    response = edit_list_request(user, list_edit_description_out_of_bounds)
    assert response.status_code == 400, response.json()
    assert response.json() == LIST_DESC_TOO_BIG

    list_edit_description_out_of_bounds.description = "     "
    list_edit_description_out_of_bounds.privacy = Clearence.ANY

    response = edit_list_request(user, list_edit_description_out_of_bounds)
    assert response.status_code == 400, response.json()
    assert response.json() == LIST_DESC_BLANK

    assert_privacy(user, list_edit_description_out_of_bounds, privacy=Clearence.OWNER)


def test_edit_list_name_out_of_bounds_returns_400(users, create_list, edit_list_request):
    """Alice tenta renomear sua lista para um nome muito grande, e depois para um nome vazio"""

    user = users["Alice"]
    list_edit_name_out_of_bounds = create_list(user, privacy=Clearence.OWNER)
    list_edit_name_out_of_bounds.name = user.username * 100
    list_edit_name_out_of_bounds.privacy=Clearence.ANY

    response = edit_list_request(user, list_edit_name_out_of_bounds)
    assert response.status_code == 400, response.json()
    assert response.json() == LIST_NAME_TOO_BIG

    list_edit_name_out_of_bounds.name = "    "
    list_edit_name_out_of_bounds.privacy=Clearence.ANY

    response = edit_list_request(user, list_edit_name_out_of_bounds)
    assert response.status_code == 400, response.json()
    assert response.json() == LIST_NAME_BLANK

    assert_privacy(user, list_edit_name_out_of_bounds, privacy=Clearence.OWNER)
