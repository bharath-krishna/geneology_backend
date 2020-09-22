from fastapi.testclient import TestClient


class CustomClient(TestClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        return super().request(*args, **kwargs)
