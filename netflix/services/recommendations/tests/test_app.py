import app as recommendations


def client():
    return recommendations.app.test_client()


def test_recommendations_list():
    body = client().get("/recommendations").get_json()
    assert "Wednesday" in body["titles"]
    assert body["service"] == "recommendations"


def test_health_version_error_metrics():
    assert client().get("/health").status_code == 200
    assert client().get("/version").get_json()["service"] == "recommendations"
    assert client().get("/error").status_code == 500
    text = client().get("/metrics").get_data(as_text=True)
    assert "http_request_duration_seconds" in text
