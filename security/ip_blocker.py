import os

from flask import Flask, jsonify, request

app = Flask(__name__)
blocked_ips = {
    item.strip()
    for item in os.environ.get("BLOCKED_IPS", "").split(",")
    if item.strip()
}


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/check")
def check():
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    client_ip = forwarded_for.split(",")[0].strip() or request.remote_addr
    if client_ip in blocked_ips:
        return jsonify(error="Forbidden"), 403
    return "", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
