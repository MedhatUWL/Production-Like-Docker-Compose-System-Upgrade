import os
import socket

import pymysql
import redis
from flask import Flask, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

app = Flask(__name__)
requests_total = Counter("http_requests_total", "HTTP requests", ["path", "method"])
cache = redis.from_url(os.environ["REDIS_URL"], decode_responses=True)


def database_value():
    connection = pymysql.connect(host=os.environ["MYSQL_HOST"], user=os.environ["MYSQL_USER"], password=os.environ["MYSQL_PASSWORD"], database=os.environ["MYSQL_DATABASE"], connect_timeout=3)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT message FROM demo LIMIT 1")
            return cursor.fetchone()[0]
    finally:
        connection.close()


@app.before_request
def count_request():
    requests_total.labels(request.path, request.method).inc()
    if request.path.startswith("/api/") and request.path != "/api/health" and request.headers.get("X-API-KEY") != os.environ["API_KEY"]:
        return jsonify(error="Unauthorized"), 401


@app.get("/api/health")
def health():
    return jsonify(status="ok", instance=socket.gethostname())


@app.get("/api/items")
def items():
    cached = cache.get("demo:item")
    if cached:
        return jsonify(source="redis", value=cached, instance=socket.gethostname())
    value = database_value()
    cache.setex("demo:item", 60, value)
    return jsonify(source="mysql", value=value, instance=socket.gethostname())


@app.get("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
