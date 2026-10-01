from math import ceil

from .utils import *

# users é um fixture definido em tests/conftest.py
# follow é um fixture definido em tests/conftest.py
# unfollow é um fixture definido em tests/conftest.py
# insert_account é um fixture definido em tests/conftest.py

def test_follow_returns_200(users, follow):
    """Alice segue Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_FOLOWING_MSG
    assert_follow(user1, user2)


def test_unfollow_returns_200(users, unfollow):
    """Alice dessegue Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unfollow(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert response.json() == SUCCESS_UNFOLOWING_MSG
    assert_unfollow(user1, user2)


def test_follow_twice_returns_200_twice(users, follow):
    """Alice segue Bernardo 2 vezes"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)

    response = follow(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)


def test_unfollow_someone_not_followed_returns_200(users, unfollow):
    """Alice dessegue Bernardo sem antes segui-lo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unfollow(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_unfollow(user1, user2)


def test_follow_someone_that_doenst_exist_returns_404(users, follow):
    """Alice segue inexistente"""

    user1, inexistent = users["Alice"], {"user_id": "inexistente"}

    response = follow(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unfollow_someone_that_doenst_exist_returns_404(users, unfollow):
    """Alice dessegue inexistente"""

    user1, inexistent = users["Alice"], {"user_id": "inexistente"}
    
    response = unfollow(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_following_yourself_returns_403(users, follow):
    """Alice segue Alice"""

    user1, user2 = users["Alice"], users["Alice"]

    response = follow(user1, user2, False)
    assert response.status_code == 403, response.json()
    assert response.json() == {"message":"O usuário não pode seguir a si mesmo!"}
    assert_unfollow(user1, user2)


def test_follow_page_has_all_fields(users):
    """Verifica se as páginas tem os campos corretos, mesmo sem que haja relações para o usuário"""

    user1 = users["Alice"]

    # Campos de uma pagina de resultados
    page_fields = ("total", "page_size", "previous_page", "current_page", "next_page", "content")

    # Pega uma página de seguidos do user1
    response_followeds = requests.get(BASE_URL + "/follow/followeds", cookies=user1["cookies"])
    assert response_followeds.status_code == 200, response_followeds.json()
    page_followeds = response_followeds.json()

    # Pega uma página de seguidores do user1
    response_followers = requests.get(BASE_URL + "/follow/followers", cookies=user1["cookies"])
    assert response_followers.status_code == 200, response_followers.json()
    page_followers = response_followers.json()

    # Verifica que a página tem todos os dados
    for pf in page_fields:
        assert pf in page_followeds.keys(), pf
        assert pf in page_followers.keys(), pf


def test_follow_page_has_all_fields_after_follow(users, follow):
    """Verifica se as páginas tem os campos corretos"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)

    # Campos de uma pagina de resultados
    page_fields = ("total", "page_size", "previous_page", "current_page", "next_page", "content")

    # Pega uma página de seguidos do user1
    response_followeds = requests.get(BASE_URL + "/follow/followeds", cookies=user1["cookies"])
    assert response_followeds.status_code == 200, response_followeds.json()
    page_followeds = response_followeds.json()

    # Pega uma página de seguidores do user2
    response_followers = requests.get(BASE_URL + "/follow/followers", cookies=user2["cookies"])
    assert response_followers.status_code == 200, response_followers.json()
    page_followers = response_followers.json()

    # Verifica que a página tem todos os dados
    for pf in page_fields:
        assert pf in page_followeds.keys(), pf
        assert pf in page_followers.keys(), pf

    # Campos do conteúdo de uma página
    content_fields = ("user_id", "username", "pfp")

    content_followeds = page_followeds["content"]
    content_followers = page_followers["content"]

    # Verifica que o conteúdo da página tem todos os dados
    for cf in content_fields:
        assert cf in content_followeds[0].keys(), cf
        assert cf in content_followers[0].keys(), cf


def test_pagination_page_size_matches_followers_and_followeds(users, follow):
    """Testa que os tamanhos de páginas estão condizentes com os dados buscados"""

    accounts = (users["Alice"], users["Bernardo"], users["Caua"], users["Daniela"])
    relationships = [[1, 2, 3], [2, 3], [3], []]
    relationship_counts = [[0, 0], [0, 0], [0, 0], [0, 0]]

    page_size = 5

    for follower, followeds in enumerate(relationships):
        for followed in followeds:
            response = follow(accounts[follower], accounts[followed], True)
            assert response.status_code == 200, response.json()
            assert_follow(accounts[follower], accounts[followed])

            relationship_counts[follower][0] += 1
            relationship_counts[followed][1] += 1

    for i, rc in enumerate(relationship_counts):
        response_followeds = requests.get(BASE_URL + f"/follow/followeds?page_size={page_size}", cookies=accounts[i]["cookies"])
        assert response_followeds.status_code == 200, response_followeds.json()
        page_followeds = response_followeds.json()
        assert page_followeds["page_size"] == rc[0]
        assert len(page_followeds["content"]) == rc[0]

        response_followers = requests.get(BASE_URL + f"/follow/followers?page_size={page_size}", cookies=accounts[i]["cookies"])
        assert response_followers.status_code == 200, response_followers.json()
        page_followers = response_followers.json()
        assert page_followers["page_size"] == rc[1]
        assert len(page_followers["content"]) == rc[1]


def test_follows_forward_pagination_covers_all_data(users, insert_account, follow):
    """Testa que percorrer as páginas usando os cursores de next_page não deixa nenhum dado pra trás"""

    user1 = users["Alice"]

    how_many_users = 7
    page_size = 3

    usernames = ["Aa" + str(nums) for nums in range(1000, 1000 + how_many_users)]
    info = [[], []]

    for u in usernames:
        user = insert_account(u)
        follow(user1, user, True)
        assert_follow(user1, user)
        info[0].append(user["username"])
        info[1].append(user["username"])

    urls = [
        f"{BASE_URL}/follow/followeds?page_size={page_size}",
        f"{BASE_URL}/follow/followeds?page_size={page_size}"
    ]

    num_pages = ceil(how_many_users/page_size)

    for i in range(2):

        url = urls[i]

        # Percorre a quantidade de páginas esperadas
        for np in range(num_pages):

            # Garante que o cursor não estourou
            assert url is not None, np

            # Pega uma página 
            response = requests.get(url, cookies=user1["cookies"])
            assert response.status_code == 200, response.json()
            page = response.json()

            content = page["content"]
            for c in content:
                if c["username"] in info[i]:
                    info[i].remove(c["username"])

            url = page["next_page"]
        
        # Garante que todos os seguidos ou seguidores foram retornados
        assert len(info[i]) == 0


def test_follows_backward_pagination_covers_all_data(users, insert_account, follow):
    """Testa que percorrer as páginas usando os cursores de previous_page não deixa nenhum dado pra trás"""

    user1 = users["Alice"]

    how_many_users = 7
    page_size = 3

    usernames = ["Aa" + str(nums) for nums in range(1000, 1000 + how_many_users)]
    info = [[], []]

    for u in usernames:
        user = insert_account(u)
        follow(user1, user, True)
        assert_follow(user1, user)
        info[0].append(user["username"])
        info[1].append(user["username"])

    urls = [
        f"{BASE_URL}/follow/followeds?page_size={page_size}",
        f"{BASE_URL}/follow/followeds?page_size={page_size}"
    ]

    num_pages = ceil(how_many_users/page_size)

    for i in range(2):

        url = urls[i]

        for _ in range(num_pages):
    
            response = requests.get(url, cookies=user1["cookies"])
            assert response.status_code == 200, response.json()

            page = response.json()

            url = page["next_page"]
        
        url = page["previous_page"]

        for _ in range(num_pages, 0, -1):

            response = requests.get(url, cookies=user1["cookies"])
            assert response.status_code == 200, response.json()

            page = response.json()

            content = page["content"]
            for c in content:
                if c["username"] in info[i]:
                    info[i].remove(c["username"])

            url = page["previous_page"]

        assert len(info[i]) == 0

