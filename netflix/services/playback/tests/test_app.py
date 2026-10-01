import json

import app as playback


def client():
    return playback.app.test_client()


class _Body:
    def __init__(self, payload):
        self._raw = json.dumps(payload).encode()

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


def test_play_uses_recommendations(monkeypatch):
    payload = {"titles": ["Wednesday", "Bridgerton"]}
    monkeypatch.setattr(playback.urllib.request, "urlopen", lambda *_a, **_k: _Body(payload))
    body = client().get("/play?title=Wednesday").get_json()
    assert body["degraded"] is False
    assert body["recommendations"] == ["Wednesday", "Bridgerton"]
    assert body["status"] == "playing"


def test_play_falls_back_when_recommendations_fail(monkeypatch):
    def _boom(*_a, **_k):
        raise playback.urllib.error.URLError("timeout")

    monkeypatch.setattr(playback.urllib.request, "urlopen", _boom)
    body = client().get("/play").get_json()
    assert body["degraded"] is True
    assert "Stranger Things" in body["recommendations"]


def test_health_metrics_error():
    assert client().get("/health").status_code == 200
    assert client().get("/error").status_code == 500
    text = client().get("/metrics").get_data(as_text=True)
    assert "http_requests_total" in text
