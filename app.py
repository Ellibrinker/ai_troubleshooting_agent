from typing import Any

from flask import Flask, jsonify, render_template, request

from analyzer import analyze_log

app = Flask(__name__)


@app.get("/")
def home() -> Any:
    return render_template("index.html")


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"}), 200


@app.post("/analyze")
def analyze() -> Any:
    data = request.get_json(silent=True) or {}

    log_text = data.get("log_text", "").strip()
    source = data.get("source", "unknown")
    environment = data.get("environment", "unknown")
    timestamp = data.get("timestamp")

    if not log_text:
        return jsonify({"error": "Missing required field: log_text"}), 400

    result = analyze_log(
        log_text=log_text,
        source=source,
        environment=environment,
        timestamp=timestamp,
    )
    return jsonify(result), 200


@app.post("/analyze/batch")
def analyze_batch() -> Any:
    data = request.get_json(silent=True) or {}
    logs = data.get("logs")

    if not isinstance(logs, list) or not logs:
        return jsonify({"error": "Missing or invalid field: logs"}), 400

    results = []

    for item in logs:
        if not isinstance(item, dict):
            continue

        log_text = str(item.get("log_text", "")).strip()
        if not log_text:
            continue

        source = item.get("source", "unknown")
        environment = item.get("environment", "unknown")
        timestamp = item.get("timestamp")

        result = analyze_log(
            log_text=log_text,
            source=source,
            environment=environment,
            timestamp=timestamp,
        )
        results.append(result)

    return jsonify({"results": results, "count": len(results)}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)