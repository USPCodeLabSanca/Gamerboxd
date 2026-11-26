import pytest
import requests
from dataclasses import asdict

from ..utils import Clearence, BASE_URL_REVIEWS, NOT_LOGGED_IN_MSG, REVIEW_NOT_FOUND_MSG
from .utils import (
    RATING_TEXT_TOO_BIG_MSG,
    RATING_TEXT_BLANK_MSG, 
    RATING_NUM_INVALID_MSG, 
    REVIEW_PRIVACY_INVALID_MSG,
    TIME_PLAYED_INVALID_MSG,
    LACK_OF_REVIEW_OWNERSHIP_MSG
)


@pytest.mark.parametrize("field, new_value, expected_status, expected_body", [
    pytest.param("rating_num", 3.5, 200, None, id="rating_num ok as float"),
    pytest.param("rating_num", 2, 200, None, id="rating_num ok as int"),
    pytest.param("rating_num", 0.0, 200, None, id="rating_num as float at inferior limit"),
    pytest.param("rating_num", 0, 200, None, id="rating_num as int at inferior limit"),
    pytest.param("rating_num", 5.0, 200, None, id="rating_num as float at superior limit"),
    pytest.param("rating_num", 5, 200, None, id="rating_num as int at superior limit"),
    pytest.param("rating_num", 6.0, 422, RATING_NUM_INVALID_MSG, id="rating_num above superior limit"),
    pytest.param("rating_num", -1, 422, RATING_NUM_INVALID_MSG, id="rating_num below inferior limit"),
    pytest.param("rating_num", 1.49, 422, RATING_NUM_INVALID_MSG, id="rating_num with wrong increment"),
    pytest.param("rating_num", "pouco", 422, None, id="rating_num as str"),
    pytest.param("rating_num", None, 422, None, id="rating_num as null"),
    pytest.param("rating_text", "Gostei desse game", 200, None, id="rating_text ok"),
    pytest.param("rating_text", "Gostei desse game 👍", 200, None, id="rating_text with emoji"),
    pytest.param("rating_text", "Gostei desse game   ", 200, None, id="rating_text with trailing space"),
    pytest.param("rating_text", "Gostei"*50, 200, None, id="rating_text at superior character limit"),
    pytest.param("rating_text", None, 200, None, id="rating_text as null"),
    pytest.param("rating_text", "Gostei"*51, 400, RATING_TEXT_TOO_BIG_MSG, id="rating_text too long"),
    pytest.param("rating_text", "         ", 400, RATING_TEXT_BLANK_MSG, id="rating_text as blank space"),
    pytest.param("rating_text", 4220, 422, None, id="rating_text as int"),
    pytest.param("privacy", Clearence.ANY, 200, None, id="privacy at min"),
    pytest.param("privacy", Clearence.FOLLOWED, 200, None, id="privacy at med"),
    pytest.param("privacy", Clearence.OWNER, 200, None, id="privacy at max"),
    pytest.param("privacy", 21, 422, REVIEW_PRIVACY_INVALID_MSG, id="privacy invalid"),
    pytest.param("privacy", "secret", 422, None, id="privacy as str"),
    pytest.param("privacy", None, 422, None, id="privacy as null"),
    pytest.param("time_played", 10, 200, None, id="time played ok"),
    pytest.param("time_played", None, 200, None, id="time played as null"),
    pytest.param("time_played", -1, 400, TIME_PLAYED_INVALID_MSG, id="time played negative"),
    pytest.param("time_played", 4.5, 422, None, id="time played as float"),
    pytest.param("time_played", "lots", 422, None, id="time_played as str"),
    pytest.param("liked", True, 200, None, id="liked ok as bool"),
    pytest.param("liked", 1, 200, None, id="liked ok as int"),
    pytest.param("liked", None, 422, None, id="liked as null"),
    pytest.param("completed", False, 200, None, id="completed ok as bool"),
    pytest.param("completed", 0, 200, None, id="completed ok as int"),
    pytest.param("completed", None, 422, None, id="completed as null"),
])
def test_editing_review_checks_edge_cases(users, create_review, edit_review_request, field, new_value, expected_status, expected_body):
    """Alice cria uma review e edita a nota numérica"""

    editor = users("Alice")
    review = create_review(editor)
    review_edit = asdict(review)

    review_edit[field] = new_value

    edit_response = edit_review_request(editor, review_edit)
    assert edit_response.status_code == expected_status, edit_response.json()

    if expected_status == 200:
        if type(new_value) == str:
            assert edit_response.json()[field].strip() == review_edit[field].strip()

        else:
            assert edit_response.json()[field] == review_edit[field]

    elif expected_body is not None:
        assert edit_response.json() == expected_body


@pytest.mark.parametrize("field_to_remove", ["rating_num", "privacy", "liked", "completed"])
def test_not_sending_all_fields_when_editing_review_returns_422(users, create_review, edit_review_request, field_to_remove):
    """Alice tenta editar sua review, mas não envia todos os campos necessários"""

    editor = users("Alice")
    review = asdict(create_review(editor))
    review.pop(field_to_remove)

    response = edit_review_request(editor, review)
    assert response.status_code == 422, response.json()


def test_edit_review_not_found_returns_404(users, create_review, edit_review_request):
    """Alice tenta editar uma review que não existe"""

    editor = users("Alice")
    review = create_review(editor)
    review.review_id = "abc"

    edit_response = edit_review_request(editor, asdict(review))
    assert edit_response.status_code == 404, edit_response.json()
    assert edit_response.json() == REVIEW_NOT_FOUND_MSG


def test_editing_review_while_not_logged_in_returns_401():
    """Um usuário tenta editar uma review sem enviar os seus cookies de autenticação"""

    response = requests.put(BASE_URL_REVIEWS + "/abc", json={"rating_num":2})
    assert response.status_code == 401, response.json()
    assert response.json() == NOT_LOGGED_IN_MSG


def test_someone_elses_review_returns_403(users, create_review, edit_review_request):
    """Alice cria uma review, Bernardo tenta editar a review de Alice"""

    creator, editor = users("Alice"), users("Bernardo")
    review = create_review(creator)
    review.rating_num = 3.5

    edit_response = edit_review_request(editor, asdict(review))
    assert edit_response.status_code == 403, edit_response.json()
    assert edit_response.json() == LACK_OF_REVIEW_OWNERSHIP_MSG




