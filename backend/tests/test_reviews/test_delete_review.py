from ..utils import REVIEW_NOT_FOUND_MSG
from .utils import SUCCESS_DELETING_MSG, LACK_OF_REVIEW_OWNERSHIP_MSG, assert_review_unlike_by_user

def test_deleting_list_returns_200(users, create_review, delete_review_request, get_review_request):
    """Alice cria e deleta uma review"""

    creator = users("Alice")
    review = create_review(creator, cleanup=False)

    delete_response = delete_review_request(creator, review)
    assert delete_response.status_code == 200, delete_response.json()
    assert delete_response.json() == SUCCESS_DELETING_MSG

    get_response = get_review_request(creator, review)
    assert get_response.status_code == 404, get_response.json()
    assert get_response.json() == REVIEW_NOT_FOUND_MSG


def test_deleting_review_twice_returns_404(users, create_review, delete_review_request):
    """Alice cria e deleta uma review e tenta deletar uma segunda vez"""

    creator = users("Alice")
    review = create_review(creator, cleanup=False)

    delete_response = delete_review_request(creator, review)
    assert delete_response.status_code == 200, delete_response.json()

    delete_response = delete_review_request(creator, review)
    assert delete_response.status_code == 404, delete_response.json()
    assert delete_response.json() == REVIEW_NOT_FOUND_MSG


def test_deleting_list_you_dont_own_returns_403(users, create_review, delete_review_request):
    """Alice cria uma review, Bernardo tenta deletar a review de Alice"""

    creator, deleter = users("Alice"), users("Bernardo")
    review = create_review(creator)   
    
    delete_response = delete_review_request(deleter, review)
    assert delete_response.status_code == 403, delete_response.json()
    assert delete_response.json() == LACK_OF_REVIEW_OWNERSHIP_MSG


def test_deleting_review_cascades_to_review_likes(users, create_review, like_review_request, delete_review_request):
    """Alice cria uma review, Bernardo curte a review, Alice deleta a review"""

    creator, liker = users("Alice"), users("Bernardo")
    review = create_review(creator, cleanup=False)

    like_response = like_review_request(liker, review)
    assert like_response.status_code == 200, like_response.json()

    delete_response = delete_review_request(creator, review)
    assert delete_response.status_code == 200, delete_response.json()
    assert_review_unlike_by_user(liker, creator, review)