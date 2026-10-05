from math import ceil
from .utils import *

# users é um fixture definido em tests/conftest.py
# block é um fixture definido em tests/conftest.py
# unblock é um fixture definido em tests/conftest.py
# follow_request é um fixture definido em tests/conftest.py

def test_blocking_returns_200(users, block):
    """Alice bloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_BLOCKING_MSG
    assert_block(user1, user2)


def test_unblocking_returns_200(users, unblock):
    """Alice desbloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unblock(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNBLOCKING_MSG
    assert_unblock(user1, user2)


def test_blocking_twice_returns_200_twice(users, block):
    """Alice bloqueia Bernardo 2 vezes"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)


def test_unblocking_someone_not_blocked_returns_200(users, unblock):
    """Alice desbloqueia Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unblock(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_unblock(user1, user2)


def test_blocking_someone_that_doenst_exist_returns_404(users, block):
    """Alice bloqueia inexistente"""

    user1, inexistent = users["Alice"], {"user_id": "inexistente"}

    response = block(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unblocking_someone_that_doenst_exist_returns_404(users, unblock):
    """Alice desbloqueia inexistente"""

    user1, inexistent = users["Alice"], {"user_id": "inexistente"}

    response = unblock(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_block_yourself_returns_403(users, block):
    """Alice bloqueia Alice"""

    user1 = users["Alice"]

    response = block(user1, user1, False)
    assert response.status_code == 403, response.json()
    assert response.json() == {"message":"O usuário não pode bloquear a si mesmo!"}
    assert_unblock(user1, user1)


def test_blocking_stops_follow(users, block, follow_request):
    """Alice bloqueia Bernardo, Bernardo segue Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)

    user1, user2 = user2, user1

    response = follow_request(user1, user2, False)
    assert response.status_code == 403, response.json()
    assert response.json() == {"message":"O usuário está tentando seguir alguém que o bloqueou!"}
    assert_unfollow(user1, user2)


def test_blocking_removes_follow(users, follow_request, block):
    """Alice segue Bernardo, Bernardo bloqueia Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow_request(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)

    user1, user2 = user2, user1

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_block(user1, user2)
    assert_unfollow(user2, user1)


def test_block_page_has_all_fields(users):
    """Verifica se as páginas tem os campos corretos, mesmo sem que haja relações para o usuário"""

    user1 = users["Alice"]

    # Campos de uma pagina de resultados
    page_fields = ("total", "page_size", "previous_page", "current_page", "next_page", "content")

    # Pega uma página de bloqueados pelo user1
    response = requests.get(BASE_URL + "/block", cookies=user1["cookies"])
    assert response.status_code == 200, response.json()
    page = response.json()

    # Verifica que a página tem todos os dados
    for pf in page_fields:
        assert pf in page.keys(), pf


def test_block_page_has_all_fields_after_block(users, block):
    """Verifica se as páginas tem os campos corretos"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = block(user1, user2, True)
    assert response.status_code == 200, response.json()

    # Campos de uma pagina de resultados
    page_fields = ("total", "page_size", "previous_page", "current_page", "next_page", "content")

    # Pega uma página de bloqueados pelo user1
    response = requests.get(BASE_URL + "/block", cookies=user1["cookies"])
    assert response.status_code == 200, response.json()
    page = response.json()

    # Verifica que a página tem todos os dados
    for pf in page_fields:
        assert pf in page.keys(), pf

    # Campos do conteúdo de uma página
    content_fields = ("user_id", "username", "pfp")

    content = page["content"]

    # Verifica que o conteúdo da página tem todos os dados
    for cf in content_fields:
        assert cf in content[0].keys(), cf


def test_pagination_page_size_matches_blocks(users, block):
    """Testa que os tamanhos de páginas estão condizentes com os dados buscados"""

    accounts = (users["Alice"], users["Bernardo"], users["Caua"], users["Daniela"])
    relationships = [[1, 2, 3], [2, 3], [3], []]
    relationship_counts = [0, 0, 0, 0]

    page_size = 5

    for blocker, blockeds in enumerate(relationships):
        for blocked in blockeds:
            response = block(accounts[blocker], accounts[blocked], True)
            assert response.status_code == 200, response.json()

            relationship_counts[blocker] += 1

    for i, rc in enumerate(relationship_counts):
        response = requests.get(BASE_URL + f"/block?page_size={page_size}", cookies=accounts[i]["cookies"])
        assert response.status_code == 200, response.json()
        page = response.json()
        assert page["page_size"] == rc
        assert len(page["content"]) == rc
        assert page["total"] == rc


def test_block_pagination_page_count(users, insert_account, block):
    user1 = users["Alice"]
    
    num_blocks = 21
    page_size = 4

    users_to_block = ["Aa" + str(nums) for nums in range(1000, 1000 + num_blocks)]

    for user in users_to_block:
        user = insert_account(user)
        block_response = block(user1, user, True)
        assert block_response.status_code == 200, block_response.json()

    num_pages = ceil(num_blocks/page_size)

    url = f"{BASE_URL}/block?page_size={page_size}"

    seen_users = []

    for pg in range(num_pages):
        assert url is not None, pg

        # Pega uma página 
        response = requests.get(url, cookies=user1["cookies"])
        assert response.status_code == 200, (response.json(), pg)
        page = response.json()
        assert page["total"] == num_blocks
        assert page["page_size"] <= page_size

        if pg == 0:
            assert page["previous_page"] is None, pg
    
        else:
            assert page["previous_page"] is not None, page

        if pg == num_pages-1:
            assert page["next_page"] is None, pg

        else:
            assert page["next_page"] is not None, pg

        assert url == page["current_page"], pg
        
        for c in page["content"]:
            assert c["username"] not in seen_users
            seen_users.append(c["username"])

        url = page["next_page"]

    assert url is None            


def test_blocks_forward_pagination_covers_all_data(users, insert_account, block):
    """Testa que percorrer as páginas usando os cursores de next_page não deixa nenhum dado pra trás"""

    user1 = users["Alice"]

    num_blocks = 7
    page_size = 3

    usernames = ["Aa" + str(nums) for nums in range(1000, 1000 + num_blocks)]
    info = []

    for u in usernames:
        user = insert_account(u)
        block_response = block(user1, user, True)
        assert block_response.status_code == 200, block_response.json()
        info.append(user["username"])

    url = f"{BASE_URL}/block?page_size={page_size}"

    num_pages = ceil(num_blocks/page_size)

    # Percorre a quantidade de páginas esperadas
    for _ in range(num_pages):

        # Pega uma página 
        response = requests.get(url, cookies=user1["cookies"])
        assert response.status_code == 200, response.json()
        page = response.json()
        assert page["total"] == num_blocks

        content = page["content"]
        for c in content:
            if c["username"] in info:
                info.remove(c["username"])

        url = page["next_page"]
    
    # Garante que todos os bloqueados foram retornados
    assert len(info) == 0


def test_blocks_backward_pagination_covers_all_data(users, insert_account, block):
    """Testa que percorrer as páginas usando os cursores de previous_page não deixa nenhum dado pra trás"""

    user1 = users["Alice"]

    num_blocks = 7
    page_size = 3

    usernames = ["Aa" + str(nums) for nums in range(1000, 1000 + num_blocks)]
    info = []

    for u in usernames:
        user = insert_account(u)
        block_response = block(user1, user, True)
        assert block_response.status_code == 200, block_response.json()
        info.append(user["username"])

    url = f"{BASE_URL}/block?page_size={page_size}"

    num_pages = ceil(num_blocks/page_size)

    # Percorre a quantidade de páginas esperadas
    for _ in range(num_pages):

        # Pega uma página 
        response = requests.get(url, cookies=user1["cookies"])
        assert response.status_code == 200, response.json()
        page = response.json()
        assert page["total"] == num_blocks

        # Avança o cursor
        url = page["next_page"]

    url = page["previous_page"]

    for _ in range(num_pages):

        # Pega uma página 
        response = requests.get(url, cookies=user1["cookies"])
        assert response.status_code == 200, response.json()
        page = response.json()

        content = page["content"]
        for c in content:
            if c["username"] in info:
                info.remove(c["username"])

        # Volta o cursor
        url = page["previous_page"]

    # Garante que todos os bloqueados foram retornados
    assert len(info) == 0


