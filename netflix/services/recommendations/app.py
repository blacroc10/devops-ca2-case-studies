"""Recommendations service. Playback treats this as a dependency it can survive without."""

import os
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SERVICE = "recommendations"
VERSION = os.environ.get("APP_VERSION", "v1")
TITLES = ["The Night Agent", "One Piece", "Bridgerton", "Wednesday"]

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


@app.get("/recommendations")
def recommendations():
    return jsonify(titles=TITLES, version=VERSION, service=SERVICE)
