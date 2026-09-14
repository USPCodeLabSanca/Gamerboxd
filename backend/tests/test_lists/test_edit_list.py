from . import BASE_URL, pytest, requests
from .utils import *
from .test_save_list import save_list_request, assert_save, assert_unsave


def edit_list(user: dict, old_list_name: str, new_list: dict):
    return requests.put(
        url=BASE_URL + f"/{old_list_name}",
        cookies=user["cookies"],
        json=new_list
    )


# ========= Testes ===========

def test_edit_list_name_to_not_used_one(users):
    """Alice cria uma lista e troca o seu nome para um nome não utilizado"""

    user = users["Alice"]
    list_in = create_list(user)
    new_list_in = {**list_in}
    new_list_in["name"] = "Nova Lista da Alice"

    response = edit_list(user, list_in["name"], new_list_in)
    assert response.status_code == 200
    assert response.json()["name"] == "Nova Lista da Alice"

    delete_list(user, new_list_in)


def test_edit_list_name_to_used_one(users):
    """Alice cria duas listas e tenta renomear a segunda para o nome da primeira"""

    user = users["Alice"]
    list_in = create_list(user)
    second_list_in = create_list(user, list_name="Segunda Lista")

    response = edit_list(user, second_list_in["name"], list_in)
    assert response.status_code == 409
    assert response.json() == {"message": f'O usuário já possui uma lista com o nome "{list_in["name"]}"!'}

    delete_list(user, list_in)
    delete_list(user, second_list_in)


def test_edit_list_description(users):
    """Bernardo cria uma lista e adiciona uma descrição a ela"""

    user = users["Bernardo"]
    list_in = create_list(user)
    new_list_in = {**list_in, "description": "Minha lista favorita de jogos"}

    response = edit_list(user, list_in["name"], new_list_in)
    assert response.status_code == 200
    assert response.json()["description"] == "Minha lista favorita de jogos"

    delete_list(user, new_list_in)


def test_edit_list_description_out_of_bounds(users):
    """Caua tenta colocar uma descrição muito grande na sua lista, e depois uma descrição vazia"""

    user = users["Caua"]
    list_in = create_list(user)
    list_in_description_too_long = {**list_in, "description": user["username"] * 100 }
    list_in_description_empty = {**list_in, "description": "    " }

    response = edit_list(user, list_in["name"], list_in_description_too_long)
    assert response.status_code == 400
    assert response.json() == {"message": "A descrição da lista não pode exceder 300 caractéres!"}

    response = edit_list(user, list_in["name"], list_in_description_empty)
    assert response.status_code == 400
    assert response.json() == {"message": "A descrição da lista não pode ser apenas espaço vazio!"}

    delete_list(user, list_in)


def test_edit_list_name_out_of_bounds(users):
    """Daniela tenta renomear sua lista para um nome muito grande, e depois para um nome vazio"""

    user = users["Daniela"]
    list_in = create_list(user, privacy = True)
    list_in_name_too_long = {"name": user["username"] * 100, "is_private": False}
    list_in_name_empty = {"name": "      ", "is_private": False}


    response = edit_list(user, list_in["name"], list_in_name_too_long)
    assert response.status_code == 400
    assert response.json() == {"message": "O nome da lista não pode exceder 45 caractéres!"}

    response = edit_list(user, list_in["name"], list_in_name_empty)
    assert response.status_code == 400
    assert response.json() == {"message": "O nome da lista não pode ser apenas espaço vazio!"}

    assert_privacy(user, list_in, privacy = True)

    delete_list(user, list_in)


def test_edit_list_description_out_of_bounds(users):
    """Daniela tenta renomear sua lista para uma descrição muito grande, e depois para uma descrição vazia"""

    user = users["Daniela"]
    list_in = create_list(user, privacy = True)
    list_in_description_too_long = {**list_in, "description": user["username"] * 100, "is_private": False}
    list_in_description_empty = {**list_in, "description":  "      ", "is_private": False}


    response = edit_list(user, list_in["name"], list_in_description_too_long)
    assert response.status_code == 400
    assert response.json() == {"message": "A descrição da lista não pode exceder 300 caractéres!"}

    response = edit_list(user, list_in["name"], list_in_description_empty)
    assert response.status_code == 400
    assert response.json() == {"message": "A descrição da lista não pode ser apenas espaço vazio!"}

    assert_privacy(user, list_in, privacy = True)

    delete_list(user, list_in)


def test_edit_list_privacy_removes_saves(users):
    """Eduarda cria uma lista pública, Fabio a salva, Eduarda muda a lista para privada editando-a diretamente"""

    atv, pas = users["Fabio"], users["Eduarda"]
    list_in = create_list(pas)

    save_response = save_list_request(atv, pas, list_in)
    assert save_response.status_code == 200
    assert_save(atv, pas, list_in)

    list_in["is_private"] = True

    response = edit_list(pas, list_in["name"], list_in)
    assert response.status_code == 200, f"{response.json()}"
    assert response.json()["is_private"] == True

    assert_unsave(atv, pas, list_in)

    delete_list(pas, list_in)