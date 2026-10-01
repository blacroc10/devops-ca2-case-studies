"""Playback keeps streaming when recommendations time out (graceful degradation)."""

import json
import os
import time
import urllib.error
import urllib.request

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SERVICE = "playback"
VERSION = os.environ.get("APP_VERSION", "v1")
REC_URL = os.environ.get(
    "RECOMMENDATIONS_URL",
    "http://recommendations-service:8080/recommendations",
)
REC_TIMEOUT = float(os.environ.get("REC_TIMEOUT", "0.4"))
FALLBACK = ["Stranger Things", "The Crown", "Narcos"]

app = Flask(__name__)

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "path", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)


@app.before_request
def _start_timer():
    request.environ["ca2_start"] = time.perf_counter()


@app.after_request
def _record(response):
    if request.path != "/metrics":
        elapsed = time.perf_counter() - request.environ.get("ca2_start", time.perf_counter())
        status = str(response.status_code)
        REQUESTS.labels(SERVICE, request.method, request.path, status).inc()
        LATENCY.labels(SERVICE, request.method, request.path).observe(elapsed)
    return response


def fetch_recommendations():
    try:
        with urllib.request.urlopen(REC_URL, timeout=REC_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
        titles = data.get("titles") or list(FALLBACK)
        return titles, False
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return list(FALLBACK), True


@app.get("/health")
def health():
    if os.environ.get("FAIL_READY") == "1":
        return jsonify(status="not-ready", service=SERVICE), 503
    return jsonify(status="ok", service=SERVICE)


@app.get("/version")
def version():
    return jsonify(service=SERVICE, version=VERSION)


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.get("/slow")
def slow():
    try:
        ms = int(request.args.get("ms", "200"))
    except ValueError:
        ms = 200
    ms = max(0, min(ms, 5000))
    time.sleep(ms / 1000)
    return jsonify(slept_ms=ms, service=SERVICE)


@app.get("/error")
def error():
    return jsonify(error="forced", service=SERVICE), 500


@app.get("/play")
def play():
    title = request.args.get("title", "House of Cards")
    titles, degraded = fetch_recommendations()
    return jsonify(
        title=title,
        status="playing",
        recommendations=titles,
        degraded=degraded,
        version=VERSION,
        service=SERVICE,
    )
