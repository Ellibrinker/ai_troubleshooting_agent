from typing import Any

from flask import Flask, jsonify, request, render_template_string

from analyzer import analyze_log

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Troubleshooting Agent</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            max-width: 900px;
        }
        h1 {
            margin-bottom: 8px;
        }
        p {
            color: #444;
        }
        textarea {
            width: 100%;
            height: 180px;
            margin-top: 12px;
            padding: 12px;
            font-family: monospace;
            font-size: 14px;
        }
        button {
            margin-top: 12px;
            padding: 10px 18px;
            font-size: 14px;
            cursor: pointer;
        }
        pre {
            background: #f6f8fa;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin-top: 20px;
        }
        .hint {
            margin-top: 8px;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <h1>AI Troubleshooting Agent</h1>
    <p>Paste a log or error message below and get possible root causes and debugging steps.</p>

    <textarea id="logInput" placeholder="Example: POST /api/orders returned 500. KeyError user_id in order_service.py"></textarea>
    <br>
    <button onclick="analyzeLog()">Analyze</button>

    <div style="margin-top:10px">
  <strong>Demo Logs:</strong><br><br>

  <button onclick="loadExample('error500')">500 Server Error</button>
  <button onclick="loadExample('auth401')">401 Unauthorized</button>
  <button onclick="loadExample('dbError')">Database Error</button>
</div>

    <div class="hint">Available API endpoints: GET /health, POST /analyze</div>

    <pre id="result">No analysis yet.</pre>

    <script>

    function loadExample(type) {
  const input = document.getElementById("logInput");

  if (type === "error500") {
    input.value = "POST /api/orders returned 500. KeyError user_id in order_service.py";
  }

  if (type === "auth401") {
    input.value = "GET /api/profile returned 401 Unauthorized. Token validation failed.";
  }

  if (type === "dbError") {
    input.value = "INSERT INTO users failed. Duplicate key constraint violation in database.";
  }
}
        async function analyzeLog() {
            const logText = document.getElementById("logInput").value;
            const resultBox = document.getElementById("result");

            if (!logText.trim()) {
                resultBox.textContent = "Please enter log text first.";
                return;
            }

            resultBox.textContent = "Analyzing...";

            try {
                const response = await fetch("/analyze", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ log_text: logText })
                });

                const data = await response.json();
                resultBox.innerHTML = `
<h3>Summary</h3>
<p>${data.summary}</p>

<h3>Probable Causes</h3>
<ul>
${data.probable_causes.map(c => `<li>${c}</li>`).join("")}
</ul>

<h3>Debugging Steps</h3>
<ul>
${data.debugging_steps.map(s => `<li>${s}</li>`).join("")}
</ul>
`;
            } catch (error) {
                resultBox.textContent = "Request failed: " + error;
            }
        }
    </script>
</body>
</html>
"""


@app.get("/")
def home() -> Any:
    return render_template_string(HTML_PAGE)


@app.get("/health")
def health() -> Any:
    return jsonify({"status": "ok"}), 200


@app.post("/analyze")
def analyze() -> Any:
    data = request.get_json(silent=True) or {}
    log_text = data.get("log_text", "").strip()

    if not log_text:
        return jsonify({"error": "Missing required field: log_text"}), 400

    result = analyze_log(log_text)
    return jsonify(result), 200


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)