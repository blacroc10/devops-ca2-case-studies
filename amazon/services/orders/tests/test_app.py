import json

import app as orders


def client():
    return orders.app.test_client()


class _Body:
    def __init__(self, payload):
        self._raw = json.dumps(payload).encode()

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_health_and_metrics():
    assert client().get("/health").status_code == 200
    assert "http_requests_total" in client().get("/metrics").get_data(as_text=True)


def test_create_order(monkeypatch):
    orders.ORDERS.clear()
    payload = {"products": [{"id": "sku-100", "name": "Kindle Paperwhite", "price": 149.99}]}
    monkeypatch.setattr(orders.urllib.request, "urlopen", lambda *_a, **_k: _Body(payload))
    response = client().post("/orders", json={"product_id": "sku-100", "qty": 2})
    assert response.status_code == 201
    assert response.get_json()["name"] == "Kindle Paperwhite"
    listed = client().get("/orders").get_json()["orders"]
    assert len(listed) == 1


def test_unknown_product(monkeypatch):
    monkeypatch.setattr(
        orders.urllib.request, "urlopen", lambda *_a, **_k: _Body({"products": []})
    )
    response = client().post("/orders", json={"product_id": "missing"})
    assert response.status_code == 404


def test_catalog_down(monkeypatch):
    def _boom(*_a, **_k):
        raise orders.urllib.error.URLError("down")

    monkeypatch.setattr(orders.urllib.request, "urlopen", _boom)
    response = client().post("/orders", json={"product_id": "sku-100"})
    assert response.status_code == 503


def test_error_route():
    assert client().get("/error").status_code == 500
