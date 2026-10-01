from .utils import *
from .test_save_list import save_list, assert_save, assert_unsave


def edit_list(user: dict, list_edit: dict):

    return requests.put(
        url=BASE_URL + f"/{list_edit["list_id"]}",
        cookies=user["cookies"],
        json=list_edit
    )

# ========= Testes ===========

def test_edit_list_name_to_not_used_one(users):
    """Alice cria uma lista e troca o seu nome para um nome não utilizado"""

    user = users["Alice"]
    list_edit = create_list(user)
    list_edit["name"] = "Nova Lista da Alice"

    response = edit_list(user, list_edit)
    assert response.status_code == 200, response.json()
    assert response.json()["name"] == "Nova Lista da Alice"

    delete_list(user, list_edit)


def test_edit_list_name_to_used_one(users):
    """Alice cria duas listas e tenta renomear a segunda para o nome da primeira"""

    user = users["Alice"]
    list1 = create_list(user)
    list2 = create_list(user, list_name="Segunda Lista")
    list2["name"] = list1["name"]

    response = edit_list(user, list2)
    assert response.status_code == 409
    assert response.json() == {"message": f'O usuário já possui uma lista com o nome "{list1["name"]}"!'}

    delete_list(user, list1)
    delete_list(user, list2)


def test_edit_list_description(users):
    """Alice cria uma lista e adiciona uma descrição a ela"""

    user = users["Alice"]
    list_edit_description = create_list(user)
    list_edit_description["description"] = "Minha lista favorita de jogos"

    response = edit_list(user, list_edit_description)
    assert response.status_code == 200
    assert response.json()["description"] == "Minha lista favorita de jogos"

    delete_list(user, list_edit_description)


def test_edit_list_description_out_of_bounds(users):
    """Alice tenta colocar uma descrição muito grande na sua lista, e depois uma descrição vazia"""

    user = users["Alice"]
    list_edit_description_out_of_bounds = create_list(user, privacy = True)
    list_edit_description_out_of_bounds["description"] = user["username"] * 100
    list_edit_description_out_of_bounds["is_private"] = False

    response = edit_list(user, list_edit_description_out_of_bounds)
    assert response.status_code == 400
    assert response.json() == {"message": "A descrição da lista não pode exceder 300 caractéres!"}

    list_edit_description_out_of_bounds["description"] = "     "
    list_edit_description_out_of_bounds["is_private"] = False

    response = edit_list(user, list_edit_description_out_of_bounds)
    assert response.status_code == 400
    assert response.json() == {"message": "A descrição da lista não pode ser apenas espaço vazio!"}

    assert_privacy(user, list_edit_description_out_of_bounds, privacy=True)

    delete_list(user, list_edit_description_out_of_bounds)


def test_edit_list_name_out_of_bounds(users):
    """Alice tenta renomear sua lista para um nome muito grande, e depois para um nome vazio"""

    user = users["Alice"]
    list_edit_name_out_of_bounds = create_list(user, privacy = True)
    list_edit_name_out_of_bounds["name"] = user["username"] * 100
    list_edit_name_out_of_bounds["is_private"] = False

    response = edit_list(user, list_edit_name_out_of_bounds)
    assert response.status_code == 400
    assert response.json() == {"message": "O nome da lista não pode exceder 45 caractéres!"}

    list_edit_name_out_of_bounds["name"] = "    "
    list_edit_name_out_of_bounds["is_private"] = False

    response = edit_list(user, list_edit_name_out_of_bounds)
    assert response.status_code == 400
    assert response.json() == {"message": "O nome da lista não pode ser apenas espaço vazio!"}

    assert_privacy(user, list_edit_name_out_of_bounds, privacy = True)

    delete_list(user, list_edit_name_out_of_bounds)


def edit_list_privacy_removes_saves(users):
    """Alice cria uma lista pública, Bernardo a salva, Alice muda a lista para privada editando-a diretamente"""

    atv, pas = users["Bernardo"], users["Alice"]
    list_in = create_list(pas)

    save_response = save_list(atv, pas, list_in)
    assert save_response.status_code == 200
    assert_save(atv, pas, list_in)

    list_in["is_private"] = True

    response = edit_list(pas, list_in)
    assert response.status_code == 200
    assert response.json()["is_private"] == True

    assert_unsave(atv, pas, list_in)

    delete_list(pas, list_in)