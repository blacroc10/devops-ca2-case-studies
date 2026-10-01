"""Amazon orders service. Calls catalog over DNS; deployed on its own."""

import json
import os
import time
import urllib.error
import urllib.request

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SERVICE = "orders"
VERSION = os.environ.get("APP_VERSION", "v1")
CATALOG_URL = os.environ.get("CATALOG_URL", "http://catalog-service:8080")

app = Flask(__name__)
ORDERS = []

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


def lookup_product(product_id):
    url = f"{CATALOG_URL.rstrip('/')}/products"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None
    for product in data.get("products", []):
        if product.get("id") == product_id:
            return product
    return {}


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


@app.post("/orders")
def create_order():
    body = request.get_json(silent=True) or {}
    product_id = body.get("product_id")
    if not product_id:
        return jsonify(error="product_id required"), 400
    try:
        qty = int(body.get("qty", 1))
    except (TypeError, ValueError):
        return jsonify(error="qty must be an integer"), 400
    if qty < 1:
        return jsonify(error="qty must be >= 1"), 400
    product = lookup_product(product_id)
    if product is None:
        return jsonify(error="catalog unavailable"), 503
    if not product:
        return jsonify(error="unknown product"), 404
    order = {
        "id": len(ORDERS) + 1,
        "product_id": product_id,
        "name": product["name"],
        "qty": qty,
        "version": VERSION,
    }
    ORDERS.append(order)
    return jsonify(order), 201


@app.get("/orders")
def list_orders():
    return jsonify(orders=ORDERS, version=VERSION, service=SERVICE)
