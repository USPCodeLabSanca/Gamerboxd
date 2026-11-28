from datetime import datetime
from uuid import uuid4

import requests

from src.models.schemas.review import ReviewOutOverview
from ..utils import BASE_URL_REVIEWS, Clearence


def read_reviews(user_id, viewer=None, **params):
    response = requests.get(
        f"{BASE_URL_REVIEWS}/created/{user_id}",
        cookies=viewer.cookies if viewer else None,
        params=params,
    )
    assert response.status_code == 200, response.json()
    page = response.json()
    assert page["page_len"] == len(page["content"])
    for review in page["content"]:
        ReviewOutOverview.model_validate(review)
        datetime.strptime(review["created_at"], "%d/%m/%Y")
        assert isinstance(review["like_count"], int)
        assert review["reviewer"]["user_id"] == user_id
    return page


def test_created_reviews_keep_received_likes_separate(users, games, create_review):
    suffix = uuid4().hex[:8]
    author = users(f"Createdauthor{suffix}")
    viewer = users(f"Createdviewer{suffix}")
    first = create_review(author, game_id=games["mario"][0])
    second = create_review(author, game_id=games["mario"][1])
    other = create_review(viewer, game_id=games["mario"][0])

    response = requests.post(f"{BASE_URL_REVIEWS}/like/{first.review_id}", cookies=viewer.cookies)
    assert response.status_code == 200, response.json()
    response = requests.post(f"{BASE_URL_REVIEWS}/like/{other.review_id}", cookies=author.cookies)
    assert response.status_code == 200, response.json()

    page = read_reviews(author.user_id, viewer)
    reviews = {review["review_id"]: review for review in page["content"]}
    assert page["total"] == 2
    assert reviews[first.review_id]["like_count"] == 1
    assert reviews[second.review_id]["like_count"] == 0
    assert reviews[first.review_id]["rel"] == 50
    assert reviews[second.review_id]["rel"] == 0
    assert reviews[first.review_id]["rating_num"] == first.rating_num
    assert reviews[first.review_id]["rating_text"] == first.rating_text
    assert reviews[first.review_id]["game"]["game_id"] == first.game_id
    assert isinstance(reviews[first.review_id]["game"]["title"], str)
    assert reviews[first.review_id]["liked"] is True
    assert reviews[first.review_id]["privacy"] == 0

    own_page = read_reviews(author.user_id, author)
    assert all(review["rel"] == 40 for review in own_page["content"])
    response = requests.delete(f"{BASE_URL_REVIEWS}/like/{first.review_id}", cookies=viewer.cookies)
    assert response.status_code == 200, response.json()
    assert all(review["like_count"] == 0 for review in read_reviews(author.user_id, viewer)["content"])


def test_created_reviews_preserve_cursor_order_search_and_privacy(users, games, create_review):
    author = users(f"Createdpage{uuid4().hex[:8]}")
    public = create_review(author, game_id=games["mario"][0])
    private = create_review(author, game_id=games["mario"][1], privacy=Clearence.OWNER)

    guest_page = read_reviews(author.user_id)
    assert guest_page["total"] == 1
    assert [review["review_id"] for review in guest_page["content"]] == [public.review_id]
    assert guest_page["content"][0]["rel"] == 0

    for order in ["created_at", "!created_at", "updated_at", "!updated_at", "title", "!title"]:
        first = read_reviews(author.user_id, author, page_size=1, order=order)
        assert first["total"] == 2
        assert first["page_len"] == 1
        assert first["next_url"] is not None
        response = requests.get(first["next_url"], cookies=author.cookies)
        assert response.status_code == 200, response.json()
        second = response.json()
        assert second["total"] == 2
        assert second["page_len"] == 1
        assert second["next_url"] is None
        assert {first["content"][0]["review_id"], second["content"][0]["review_id"]} == {public.review_id, private.review_id}
        if order.lstrip("!") == "title":
            titles = [first["content"][0]["game"]["title"], second["content"][0]["game"]["title"]]
            assert titles == sorted(titles, reverse=order.startswith("!"))

    title = guest_page["content"][0]["game"]["title"]
    searched = read_reviews(author.user_id, author, search=title)
    assert any(review["review_id"] == public.review_id for review in searched["content"])
    assert all(review["game"]["title"].lower().startswith(title.lower()) for review in searched["content"])
