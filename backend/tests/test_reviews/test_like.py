import requests

from ..utils import BaseReview, Clearence, BASE_URL_REVIEWS, NOT_LOGGED_IN_MSG, REVIEW_NOT_FOUND_MSG
from .utils import (
    PRIVATE_REVIEW_MSG, BLOCKED_BY_REVIEW_OWNER_MSG, USER_BLOCKED_REVIEW_OWNER_MSG,
    assert_review_like_by_review, assert_review_unlike_by_review,
    assert_review_like_by_user, assert_review_unlike_by_user
)

SUCCESS_LIKING_MSG = {"message": "Like adicionado com sucesso!"}
SUCCESS_UNLIKING_MSG = {"message": "Like removido com sucesso!"}


def test_liking_review_returns_200(users, create_review, like_review_request):
    """Alice cria uma review e Bernado curte a review"""

    creator, liker = users("Alice"), users("Bernardo")

    review = create_review(creator)

    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()
    assert like_response.json() == SUCCESS_LIKING_MSG
    assert_review_like_by_review(liker, creator, review)
    assert_review_like_by_user(liker, creator, review)


def test_unliking_review_returns_200(users, create_review, like_review_request, unlike_review_request):
    """Alice cria uma review, Bernado curte e depois descurte a review"""

    creator, liker = users("Alice"), users("Bernardo")

    review = create_review(creator)

    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()

    unlike_response = unlike_review_request(liker, review)
    assert unlike_response.status_code == 200, unlike_response.json()
    assert unlike_response.json() == SUCCESS_UNLIKING_MSG
    assert_review_unlike_by_review(liker, creator, review)
    assert_review_unlike_by_user(liker, creator, review)


def test_liking_your_own_review_returns_200(users, create_review, like_review_request):
    """Alice cria uma review e curte a review"""

    creator = users("Alice")
    review = create_review(creator)

    like_response = like_review_request(creator, review)
    assert like_response.status_code == 200, like_response.json()


def test_liking_twice_returns_200(users, create_review, like_review_request):
    """Alice cria uma review e Bernado curte a review 2 vezes seguidas"""

    creator, liker = users("Alice"), users("Bernardo")

    review = create_review(creator)

    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()

    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()


def test_unliking_twice_returns_200(users, create_review, like_review_request, unlike_review_request):
    """Alice cria uma review e Bernado curte a review"""

    creator, liker = users("Alice"), users("Bernardo")

    review = create_review(creator)

    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()

    unlike_response = unlike_review_request(liker, review)
    assert unlike_response.status_code == 200, unlike_response.json()

    unlike_response_twice = unlike_review_request(liker, review)
    assert unlike_response_twice.status_code == 200, unlike_response.json()

 
def test_liking_inexistent_review_returns_404(users, like_review_request):
    """Alice dá like numa review que não existe"""

    user = users("Alice")
    review = BaseReview(review_id="inexistent")

    like_response = like_review_request(user, review)
    assert like_response.status_code == 404, like_response.json()
    assert like_response.json() == REVIEW_NOT_FOUND_MSG


def test_unliking_inexistent_review_returns_404(users, unlike_review_request):
    """Alice remove o like de uma review que não existe"""

    user = users("Alice")
    review = BaseReview(review_id="inexistent")

    unlike_response = unlike_review_request(user, review)
    assert unlike_response.status_code == 404, unlike_response.json()
    assert unlike_response.json() == REVIEW_NOT_FOUND_MSG


def test_liking_private_review_returns_403(users, create_review, like_review_request):
    """Alice cria uma review privada e Bernardo tenta dar like nela"""

    creator, liker = users("Alice"), users("Bernardo")
    review = create_review(creator, privacy=Clearence.OWNER)

    like_response = like_review_request(liker, review)

    assert like_response.status_code == 403, like_response.json()
    assert like_response.json() == PRIVATE_REVIEW_MSG
    assert_review_unlike_by_review(liker, creator, review)


def test_blocking_prevents_likes_both_ways(users, create_review, block_request, like_review_request):
    """Alice e Bernardo criam reviews. Alice bloqueia Bernardo. Bernardo tenta dar like na review de Alice, e Alice tenta dar like na review de Bernardo"""

    blocker, blocked = users("Alice"), users("Bernardo")

    block_response = block_request(blocker, blocked)
    assert block_response.status_code == 200, block_response.json()

    review_blocker = create_review(blocker)
    review_blocked = create_review(blocked)

    like_response = like_review_request(blocked, review_blocker)

    assert like_response.status_code == 433, like_response.json()
    assert like_response.json() == BLOCKED_BY_REVIEW_OWNER_MSG
    assert_review_unlike_by_review(blocked, blocker, review_blocker)

    like_response = like_review_request(blocked, review_blocked)

    assert like_response.status_code == 400, like_response.json()
    assert like_response.json() == USER_BLOCKED_REVIEW_OWNER_MSG
    assert_review_unlike_by_review(blocker, blocked, review_blocked)


def test_blocking_after_liking_remove_likes(users, create_review, block_request, like_review_request):
    """Alice cria uma review, Bernardo curte a review. Quando um bloqueia o outro, os likes devem sumir."""

    blocker, blocked = users("Alice"), users("Bernardo")
    review_blocker = create_review(blocker)
    review_blocked = create_review(blocked)

    like_response1 = like_review_request(blocked, review_blocker)
    like_response2 = like_review_request(blocker, review_blocked)
    assert like_response1.status_code == 200, like_response1.json()
    assert like_response2.status_code == 200, like_response2.json()

    block_response = block_request(blocked, blocker)
    assert block_response.status_code == 200, block_response.json()

    assert_review_unlike_by_review(blocked, blocker, review_blocker)
    assert_review_unlike_by_review(blocker, blocked, review_blocked)


def test_liking_review_while_not_logged_in_returns_401():
    """Um usuário tenta curtir uma review sem enviar os seus cookies de autenticação"""

    response = requests.post(BASE_URL_REVIEWS + "/like/abc")
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_unliking_review_while_not_logged_in_returns_401():
    """Um usuário tenta descurtir uma review sem enviar os seus cookies de autenticação"""

    response = requests.delete(BASE_URL_REVIEWS + "/like/abc")
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_privacy_change_to_followed_removes_unfollowed_likes(users, create_review, update_review_request, like_review_request):
    """Alice cria uma review pública, Bernardo curte a review. Alice muda a privacidade para FOLLOWED, mas não segue Bernardo, portanto Bernardo perde o like"""

    creator, liker = users("Alice"), users("Bernardo")
    review = create_review(creator, privacy=Clearence.ANY)
    
    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()    

    update_response = update_review_request(creator, review, privacy=Clearence.FOLLOWED)
    assert update_response.status_code == 200, update_response.json()

    assert update_response.json()["like_count"] == 0
    assert_review_unlike_by_review(liker, creator, review)


def test_privacy_change_to_owner_removes_unfollowed_likes(users, create_review, update_review_request, like_review_request):
    """Alice cria uma review pública, Bernardo curte a review. Alice muda a privacidade para OWNER, portanto Bernardo perde o like"""

    creator, liker = users("Alice"), users("Bernardo")
    review = create_review(creator, privacy=Clearence.ANY)
    
    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()    

    update_response = update_review_request(creator, review, privacy=Clearence.OWNER)
    assert update_response.status_code == 200, update_response.json()

    assert update_response.json()["like_count"] == 0
    assert_review_unlike_by_review(liker, creator, review)


def test_privacy_change_to_followed_doesnt_remove_followed_likes(users, create_review, update_review_request, like_review_request, follow_request):
    """Alice cria uma review pública, Bernardo curte a review. Alice muda a privacidade para FOLLOWED, e segue Bernardo, portanto Bernardo mantém o like"""

    creator, liker = users("Alice"), users("Bernardo")
    review = create_review(creator, privacy=Clearence.ANY)
    
    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()    

    follow_response = follow_request(creator, liker)
    assert follow_response.status_code == 200, follow_response.json()

    update_response = update_review_request(creator, review, privacy=Clearence.FOLLOWED)
    assert update_response.status_code == 200, update_response.json()

    assert update_response.json()["like_count"] == 1
    assert_review_like_by_review(liker, creator, review)