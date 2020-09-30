from tests.e2e import CustomClient


def test_docs(user_client: CustomClient):
    response = user_client.get("/")
    assert response.status_code == 200


def test_me(user_client: CustomClient):
    response = user_client.get("/me")
    assert response.status_code == 200


def test_people(user_client: CustomClient):
    response = user_client.get("/people")
    assert response.status_code == 200
    json_response = response.json()
    for people in json_response['people']:
        assert people['name'] in ['demo demo']
