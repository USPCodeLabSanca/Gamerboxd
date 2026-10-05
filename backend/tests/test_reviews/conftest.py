from .utils import *

@pytest.fixture()
def create_review():
    """Insere uma review no DB e depois a remove do DB"""

    responses = []
    def _review(user: dict, game_id: int):
        review = {
            "game": game_id,
            "rating_num": 3.5,
            "rating_text": "Muito bom, recomendo!",
            "liked": True,
            "is_private": False,
            "time_played": 15.5,
            "completed": True,
        }

        # Insere a review no DB
        insert_resp = requests.post(url=BASE_URL, json=review, cookies=user["cookies"])
        responses.append({"response": insert_resp, "cookies": user["cookies"], "game_id": game_id})

        # Verifica se deu certo a inserção
        assert insert_resp.status_code == 200
        assert insert_resp.json() == SUCCESS_CREATING_MSG

        return review

    yield _review

    
    for insert_resp in responses:

        # Remove a review do DB
        del_resp = requests.delete(url=BASE_URL + f"/{insert_resp["game_id"]}", cookies=insert_resp["cookies"])

        # Verifica se deu certo remover
        assert del_resp.status_code == 200
        assert del_resp.json() == SUCCESS_DELETING_MSG


@pytest.fixture
def edit_review():
    """Faz um usuário editar sua review. reset != None significa que vai reverter o DB depois"""

    response = []

    def _edit_review(user: dict, old_game_id: int, review_in: dict, reset: dict = None):
        # Tenta editar a review no DB
        edit_resp = requests.put(f"{BASE_URL}/{old_game_id}", cookies=user["cookies"], json=review_in)
        response.append({"response": edit_resp, "reset": reset, "old_game_id": old_game_id, "cookies": user["cookies"]})
        return edit_resp

    yield _edit_review


    for edit_resp in response:

        # Reverte a review depois de editar
        if (edit_resp["reset"] is not None) and (edit_resp["response"].status_code == 200):
            old_game_id, cookies, reset = edit_resp["old_game_id"], edit_resp["cookies"], edit_resp["reset"]
            reset_resp = requests.put(f"{BASE_URL}/{old_game_id}", cookies=cookies, json=reset)
            assert reset_resp.status_code == 200