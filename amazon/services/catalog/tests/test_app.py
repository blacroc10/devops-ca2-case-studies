import app as catalog


def client():
    return catalog.app.test_client()


def test_health_ok():
    response = client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_version_reads_env(monkeypatch):
    monkeypatch.setattr(catalog, "VERSION", "v2")
    response = client().get("/version")
    assert response.get_json()["version"] == "v2"


def test_products():
    body = client().get("/products").get_json()
    assert any(item["id"] == "sku-100" for item in body["products"])


def test_error_is_500():
    assert client().get("/error").status_code == 500


def test_metrics_exposed():
    client().get("/health")
    body = client().get("/metrics").get_data(as_text=True)
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body
