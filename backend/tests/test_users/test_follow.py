from math import ceil

from .utils import *

# users é um fixture definido em tests/conftest.py
# follow_request é um fixture definido em tests/conftest.py
# unfollow é um fixture definido em tests/conftest.py
# insert_account é um fixture definido em tests/conftest.py

def test_follow_returns_200(users, follow_request):
    """Alice segue Bernardo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow_request(user1, user2, True)
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


def test_follow_twice_returns_200_twice(users, follow_request):
    """Alice segue Bernardo 2 vezes"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow_request(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)

    response = follow_request(user1, user2, True)
    assert response.status_code == 200, response.json()
    assert_follow(user1, user2)


def test_unfollow_someone_not_followed_returns_200(users, unfollow):
    """Alice dessegue Bernardo sem antes segui-lo"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = unfollow(user1, user2, False)
    assert response.status_code == 200, response.json()
    assert_unfollow(user1, user2)


def test_follow_someone_that_doenst_exist_returns_404(users, follow_request):
    """Alice segue inexistente"""

    user1, inexistent = users["Alice"], {"user_id": "inexistente"}

    response = follow_request(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_unfollow_someone_that_doenst_exist_returns_404(users, unfollow):
    """Alice dessegue inexistente"""

    user1, inexistent = users["Alice"], {"user_id": "inexistente"}
    
    response = unfollow(user1, inexistent, False)
    assert response.status_code == 404, response.json()
    assert response.json() == USER_NOT_FOUND_MSG


def test_following_yourself_returns_403(users, follow_request):
    """Alice segue Alice"""

    user1, user2 = users["Alice"], users["Alice"]

    response = follow_request(user1, user2, False)
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


def test_follow_page_has_all_fields_after_follow(users, follow_request):
    """Verifica se as páginas tem os campos corretos"""

    user1, user2 = users["Alice"], users["Bernardo"]

    response = follow_request(user1, user2, True)
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


def test_follow_pagination_page_count(users, insert_account, follow_request):
    user1 = users["Alice"]
    
    num_follows = 21
    page_size = 4

    usernames = ["Aa" + str(nums) for nums in range(1000, 1000 + num_follows)]

    for u in usernames:
        user = insert_account(u)
        follow_response = follow_request(user1, user, True)
        assert follow_response.status_code == 200, follow_response.json()
        follow_response = follow_request(user, user1, True)
        assert follow_response.status_code == 200, follow_response.json()

    num_pages = ceil(num_follows/page_size)

    urls = [f"{BASE_URL}/follow/followeds?page_size={page_size}",
        f"{BASE_URL}/follow/followers?page_size={page_size}"
    ]


    for i in range(2):

        url = urls[i]

        for pg in range(num_pages):
            assert url is not None, pg

            # Pega uma página 
            response = requests.get(url, cookies=user1["cookies"])
            assert response.status_code == 200, (response.json(), pg)
            page = response.json()
            assert page["total"] == num_follows
            assert page["page_size"] <= page_size

            if pg == 0:
                assert page["previous_page"] is None, page
        
            else:
                assert page["previous_page"] is not None, page

            if pg == num_pages-1:
                assert page["next_page"] is None, page

            else:
                assert page["next_page"] is not None, page

            assert url == page["current_page"], page

            url = page["next_page"]

        assert url is None


def test_pagination_page_size_matches_followers_and_followeds(users, follow_request):
    """Testa que os tamanhos de páginas estão condizentes com os dados buscados"""

    accounts = (users["Alice"], users["Bernardo"], users["Caua"], users["Daniela"])
    relationships = [[1, 2, 3], [2, 3], [3], []]
    relationship_counts = [[0, 0], [0, 0], [0, 0], [0, 0]]

    page_size = 5

    for follower, followeds in enumerate(relationships):
        for followed in followeds:
            response = follow_request(accounts[follower], accounts[followed], True)
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


def test_follows_forward_pagination_covers_all_data(users, insert_account, follow_request):
    """Testa que percorrer as páginas usando os cursores de next_page não deixa nenhum dado pra trás"""

    user1 = users["Alice"]

    num_follows = 7
    page_size = 3

    usernames = ["Aa" + str(nums) for nums in range(1000, 1000 + num_follows)]
    seen_users = [[], []]

    for u in usernames:
        user = insert_account(u)
        follow_response = follow_request(user1, user, True)
        assert follow_response.status_code == 200, follow_response.json()
        follow_response = follow_request(user, user1, True)
        assert follow_response.status_code == 200, follow_response.json()

    urls = [
        f"{BASE_URL}/follow/followeds?page_size={page_size}",
        f"{BASE_URL}/follow/followeds?page_size={page_size}"
    ]

    num_pages = ceil(num_follows/page_size)

    for i in range(2):

        url = urls[i]

        # Percorre a quantidade de páginas esperadas
        for np in range(num_pages):

            # Pega uma página 
            response = requests.get(url, cookies=user1["cookies"])
            assert response.status_code == 200, response.json()
            page = response.json()

            for c in page["content"]:
                assert c["username"] not in seen_users[i]
                seen_users[i].append(c["username"])

            url = page["next_page"]
        
        seen_users[i].sort()
        assert seen_users[i] == usernames


def test_follows_backward_pagination_covers_all_data(users, insert_account, follow_request):
    """Testa que percorrer as páginas usando os cursores de previous_page não deixa nenhum dado pra trás"""

    user1 = users["Alice"]

    num_follows = 7
    page_size = 3

    usernames = ["Aa" + str(nums) for nums in range(1000, 1000 + num_follows)]
    info = [[], []]

    for u in usernames:
        user = insert_account(u)
        follow_request(user1, user, True)
        assert_follow(user1, user)
        info[0].append(user["username"])
        info[1].append(user["username"])

    urls = [
        f"{BASE_URL}/follow/followeds?page_size={page_size}",
        f"{BASE_URL}/follow/followeds?page_size={page_size}"
    ]

    num_pages = ceil(num_follows/page_size)

    for i in range(2):

        url = urls[i]

        for _ in range(num_pages):
    
            response = requests.get(url, cookies=user1["cookies"])
            assert response.status_code == 200, response.json()

            page = response.json()

            url = page["next_page"]
        
        url = page["previous_page"]

        for _ in range(num_pages):

            response = requests.get(url, cookies=user1["cookies"])
            assert response.status_code == 200, response.json()

            page = response.json()

            content = page["content"]
            for c in content:
                if c["username"] in info[i]:
                    info[i].remove(c["username"])

            url = page["previous_page"]

        assert len(info[i]) == 0

