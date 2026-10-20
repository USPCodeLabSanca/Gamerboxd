from .utils import *


def test_liking_review_returns_200(users, games, create_review, like_review_request):
    """Alice cria uma review e Bernado curte a review"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id = games["GTA"][0]

    review = create_review(user1, game_id)

    like_response = like_review_request(user2, review)
    assert like_response.status_code == 200, like_response.json()
    assert like_response.json() == SUCCESS_LIKING_MSG
    assert_review_like(user2, user1, review)


def test_unliking_review_returns_200(users, games, create_review, like_review_request, unlike_review_request):
    """Alice cria uma review, Bernado curte e depois descurte a review"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id = games["GTA"][0]

    review = create_review(user1, game_id)

    like_response = like_review_request(user2, review)
    assert like_response.status_code == 200, like_response.json()

    unlike_response = unlike_review_request(user2, review)
    assert unlike_response.status_code == 200, unlike_response.json()
    assert unlike_response.json() == SUCCESS_UNLIKING_MSG
    assert_review_unlike(user2, user1, review)


def test_liking_your_own_review_returns_200(users, games, create_review, like_review_request):
    """Alice cria uma review e curte a review"""

    user1 = users["Alice"]
    game_id = games["roblox"][0]

    review = create_review(user1, game_id)

    like_response = like_review_request(user1, review)
    assert like_response.status_code == 200, like_response.json()


def test_liking_twice_returns_200(users, games, create_review, like_review_request):
    """Alice cria uma review e Bernado curte a review 2 vezes seguidas"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id = games["GTA"][0]

    review = create_review(user1, game_id)

    like_response = like_review_request(user2, review)
    assert like_response.status_code == 200, like_response.json()

    like_response_second_time = like_review_request(user2, review)
    assert like_response_second_time.status_code == 200, like_response_second_time.json()

    assert_review_like(user2, user1, review)


def test_unliking_twice_returns_200(users, games, create_review, like_review_request, unlike_review_request):
    """Alice cria uma review e Bernado curte a review"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id = games["GTA"][0]

    review = create_review(user1, game_id)

    like_response = like_review_request(user2, review)
    assert like_response.status_code == 200, like_response.json()

    unlike_response = unlike_review_request(user2, review)
    assert unlike_response.status_code == 200, unlike_response.json()

    assert_review_unlike(user2, user1, review)

    unlike_response_twice = unlike_review_request(user2, review)
    assert unlike_response_twice.status_code == 200, unlike_response.json()

    
def test_liking_inexistent_review_returns_404(users, like_review_request):
    """Alice dá like numa review que não existe"""

    user1 = users["Alice"]
    review = BaseReview(review_id="inexistent")

    like_response = like_review_request(user1, review)
    assert like_response.status_code == 404, like_response.json()
    assert like_response.json() == REVIEW_NOT_FOUND_MSG


def test_unliking_inexistent_review_returns_404(users, unlike_review_request):
    """Alice remove o like de uma review que não existe"""

    user1 = users["Alice"]
    review = BaseReview(review_id="inexistent")

    unlike_response = unlike_review_request(user1, review)
    assert unlike_response.status_code == 404, unlike_response.json()
    assert unlike_response.json() == REVIEW_NOT_FOUND_MSG


def test_liking_private_review_returns_403(users, games, create_review, like_review_request):
    """Alice cria uma review privada e Bernardo tenta dar like nela"""

    user1, user2 = users["Alice"], users["Bernardo"]
    game_id = games["mario"][0]
    review = create_review(user1, game_id, privacy=Clearence.OWNER)

    like_response = like_review_request(user2, review)

    assert like_response.status_code == 403, like_response.json()
    assert like_response.json() == PRIVATE_REVIEW_MSG
    assert_review_unlike(user2, user1, review)


def test_liking_after_block_returns_403(users, games, create_review, block_request, like_review_request):
    """Alice cria uma review, depois bloqueia Bernardo. Bernardo tenta dar like na review de Alice"""

    user1, user2 = users["Alice"], users["Bernardo"]

    block_response = block_request(user1, user2)
    assert block_response.status_code == 200, block_response

    game_id = games["mario"][0]
    review = create_review(user1, game_id)

    like_response = like_review_request(user2, review)

    assert like_response.status_code == 403, like_response.json()
    assert like_response.json() == BLOCKED_BY_REVIEW_OWNER_MSG
    assert_review_unlike(user2, user1, review)
