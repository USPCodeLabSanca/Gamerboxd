from . import *

def create_review(user, game_id):
    review = {
        "game": game_id,
        "rating_num": 8.5,
        "rating_text": "Muito bom, recomendo!",
        "liked": True,
        "is_private": False,
        "time_played": 15.5,
        "completed": True,
    }
    response = requests.post(url=BASE_URL, json=review, cookies=user["cookies"])

    assert response.status_code == 200
    assert response.json() == SUCCESS_CREATING_MSG

    return review


def delete_review(user, game_id):
    response = requests.delete(url=BASE_URL + f"/{game_id}", cookies=user["cookies"])
    assert response.status_code == 200
    assert response.json() == SUCCESS_DELETING_MSG