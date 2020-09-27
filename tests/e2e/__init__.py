from fastapi.testclient import TestClient


class CustomClient(TestClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        token = self.app.kc.token(username='demo', password='demo', grant_type=['password'])
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        kwargs['headers'] = headers
        return super().request(*args, **kwargs)
