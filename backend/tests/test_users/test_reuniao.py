from .utils import *

# users é um fixture definido em tests/conftest.py
# follow_request é um fixture definido em tests/conftest.py
# unfollow é um fixture definido em tests/conftest.py
# insert_account é um fixture definido em tests/conftest.py


def insert(username):
    payload = {"username": username, "password": f"{username}{username}1!", "email": f"{username}@gmail.com"}
        
    session = requests.Session()
    response = session.post(BASE_URL, json=payload)

    for c in session.cookies:
        c.secure = False

    response_json = response.json()

    assert response.status_code == 200, response_json

    return {**payload, "cookies": session.cookies, "user_id": response_json["id"]}
    


def test_reuniao(follow_request):

    main_user = insert("User1")

    num_follows = 50

    usernames = ["Aa" + str(nums) for nums in range(1000, 1000 + num_follows)]

    for u in usernames:
        user = insert(u)
        follow_response = follow_request(user, main_user, True)
        assert follow_response.status_code == 200

