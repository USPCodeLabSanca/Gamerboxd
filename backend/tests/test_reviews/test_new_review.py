from . import *

def base_review(**overrides):
    """Payload padrão de uma review válida. O campo 'game' é preenchido em runtime
    com um id real vindo da fixture `games`, a menos que já tenha sido sobrescrito."""
 
    review = {
        "game": -1,
        "rating_num": 8.5,
        "rating_text": "Muito bom, recomendo!",
        "liked": True,
        "is_private": False,
        "time_played": 15.5,
        "completed": True,
    }
    review.update(overrides)
    return review
 
 
new_reviews = [
    # Testes funcionais
    (base_review(), 200, SUCCESS_CREATING_MSG),
    (base_review(rating_text=None), 200, SUCCESS_CREATING_MSG),
    ({k: v for k, v in base_review().items() if k != "rating_text"}, 200, SUCCESS_CREATING_MSG),
    (base_review(liked=False, is_private=True, completed=False, time_played=0.0, rating_num=0.0), 200, SUCCESS_CREATING_MSG),
    (base_review(rating_text="a" * 300), 200, SUCCESS_CREATING_MSG),
 
    # Review duplicada (mesmo usuário, mesmo jogo)
    (base_review(), 409, {"message": "Você já possui uma review desse jogo!"}),
 
    # Texto da review excede o limite de caracteres
    (base_review(rating_text="a" * 301), 400, {"message": "O texto da review não pode exceder 300 caracteres"}),
 
    # Testes de schema inválido/mal formatado - campos obrigatórios ausentes
    ({k: v for k, v in base_review().items() if k != "game"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "rating_num"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "liked"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "is_private"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "time_played"}, 422, None),
    ({k: v for k, v in base_review().items() if k != "completed"}, 422, None),
 
    # Testes de schema inválido/mal formatado - tipos errados
    (base_review(game="abc"), 422, None),
    (base_review(game=None), 422, None),
    (base_review(rating_num="alta"), 422, None),
    (base_review(rating_text=12345), 422, None),
    (base_review(liked="talvez"), 422, None),
    (base_review(is_private=[]), 422, None),
    (base_review(time_played="muito"), 422, None),
    (base_review(completed={}), 422, None),
 
    # Corpo vazio
    ({}, 422, None),
]
 
 
@pytest.mark.parametrize("review_in,expected_status,expected_body", new_reviews)
def test_new_review(users, games, review_in, expected_status, expected_body):
    """Testa a criação de reviews: sucesso, review duplicada, texto muito longo e schema inválido"""
 
    user = users["Alice"].copy()
    cookies = user.pop("cookies")
    game_id = games["mario"][0][0]
 
    if review_in.get("game") == -1:
        review_in["game"] = game_id
 
    # Cenário de duplicidade: cria uma review antes para forçar o conflito
    if expected_status == 409:
        setup_response = requests.post(url=BASE_URL, json=base_review(game=game_id), cookies=cookies)
        assert setup_response.status_code == 200
 
    response = requests.post(url=BASE_URL, json=review_in, cookies=cookies)
    assert response.status_code == expected_status
 
    if expected_body is not None:
        assert response.json() == expected_body
 
    if response.status_code == 200:
        response_delete = requests.delete(url=BASE_URL + f"/{review_in['game']}", cookies=cookies)
        assert response_delete.status_code == 200
 
    if expected_status == 409:
        response_delete_setup = requests.delete(url=BASE_URL + f"/{game_id}", cookies=cookies)
        assert response_delete_setup.status_code == 200
