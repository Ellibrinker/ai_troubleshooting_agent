# AI Troubleshooting Agent

## Web-based debugging assistant for backend logs

AI Troubleshooting Agent is a lightweight debugging assistant for web applications.
The tool analyzes backend log messages or error text and returns structured troubleshooting insights, including detected signals, probable root causes, and recommended debugging steps.

Built with **Python** and **Flask**, the project exposes REST API endpoints for programmatic log analysis and includes a simple browser-based UI for testing.

---

# Features

* Analyze application logs and error messages
* Detect troubleshooting signals such as:

  * HTTP status codes
  * API endpoints
  * HTTP methods
  * exception types
  * authentication-related issues
  * database-related issues
  * timeout indicators
  * file names mentioned in logs
* Return structured analysis with:

  * summary
  * category
  * severity
  * probable root causes
  * debugging steps
  * extracted signals
* Includes a simple web interface for manual testing
* Supports both heuristic analysis and optional LLM-based analysis
* REST API endpoints for single-log and batch analysis

---

# Project Structure

```text
ai_troubleshooting_agent/
├── static/
│   ├── app.js
│   └── style.css
├── templates/
│   └── index.html
├── .env.example
├── .gitignore
├── analyzer.py
├── app.py
├── requirements.txt
└── run.py
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/Ellibrinker/ai_troubleshooting_agent.git
cd ai_troubleshooting_agent
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the environment.

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the project root.

Example:

```env
OPENAI_API_KEY=your_api_key_here
USE_OPENAI=false
FLASK_ENV=development
```

### Notes

* Set `USE_OPENAI=true` to enable OpenAI-based analysis
* If OpenAI is not enabled or fails, the app falls back to heuristic analysis
* The `.env` file is **not committed to Git** for security reasons

---

# Running the Application

Start the Flask server:

```bash
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

---

# API Endpoints

## Health Check

**GET /health**

Example response:

```json
{
  "status": "ok"
}
```

---

## Analyze a Single Log

**POST /analyze**

Example request:

```json
{
  "log_text": "POST /api/orders returned 500. KeyError user_id in order_service.py",
  "source": "orders-service",
  "environment": "production",
  "timestamp": "2026-03-13T10:20:00Z"
}
```

Example response:

```json
{
  "mode": "heuristic",
  "summary": "Likely issue involves backend request handling, validation, dependency behavior, or environment-specific configuration.",
  "category": "server",
  "severity": "high",
  "source": "orders-service",
  "environment": "production",
  "timestamp": "2026-03-13T10:20:00Z",
  "signals": {
    "status_codes": ["500"],
    "endpoints": ["/api/orders"],
    "exception_type": "KeyError",
    "http_method": "POST",
    "file_name": "order_service.py",
    "contains_timeout": false,
    "contains_auth": false,
    "contains_db": false,
    "contains_null_or_missing": true,
    "contains_traceback": false
  },
  "probable_causes": [
    "Unhandled server-side exception or missing validation in backend logic.",
    "Missing or malformed input data leading to null, undefined, or missing-key access.",
    "Application raised KeyError, indicating a code-path or data-handling issue."
  ],
  "debugging_steps": [
    "Inspect backend logs around the failing request and locate the full stack trace.",
    "Validate request payload fields and add guards before accessing optional or missing values.",
    "Search for the exact KeyError location in code and inspect the triggering input."
  ]
}
```

---

## Analyze Multiple Logs

**POST /analyze/batch**

Example request:

```json
{
  "logs": [
    {
      "log_text": "POST /api/orders returned 500. KeyError user_id",
      "source": "orders-service",
      "environment": "production"
    },
    {
      "log_text": "GET /api/profile returned 401 Unauthorized",
      "source": "auth-service",
      "environment": "staging"
    }
  ]
}
```

Example response:

```json
{
  "results": [
    {
      "mode": "heuristic",
      "summary": "Likely issue involves backend request handling, validation, dependency behavior, or environment-specific configuration.",
      "category": "server",
      "severity": "high",
      "source": "orders-service",
      "environment": "production",
      "timestamp": null,
      "signals": {
        "status_codes": ["500"],
        "endpoints": ["/api/orders"],
        "exception_type": "KeyError",
        "http_method": "POST",
        "file_name": null,
        "contains_timeout": false,
        "contains_auth": false,
        "contains_db": false,
        "contains_null_or_missing": true,
        "contains_traceback": false
      },
      "probable_causes": [
        "Unhandled server-side exception or missing validation in backend logic."
      ],
      "debugging_steps": [
        "Inspect backend logs around the failing request and locate the full stack trace."
      ]
    }
  ],
  "count": 1
}
```

---

# Technologies Used

* Python
* Flask
* JavaScript
* HTML
* CSS
* OpenAI API
* Gunicorn

---

# Author

**Elli Brinker**
