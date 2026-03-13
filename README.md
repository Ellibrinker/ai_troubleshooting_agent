# AI Troubleshooting Agent

## Web-based debugging assistant for backend logs

AI Troubleshooting Agent is a lightweight debugging assistant for backend systems.
The tool analyzes application logs or error messages and returns structured troubleshooting insights.

Built with **Python** and **Flask**, the project exposes REST API endpoints for programmatic log analysis and includes a simple browser-based UI for testing.

---

## Live Demo

👉 **[Live Demo](http://13.49.66.245)**

---

## Features

### Log Analysis

* Analyze application logs and error messages.

### Signal Detection

The tool automatically detects troubleshooting signals such as:

* HTTP status codes
* API endpoints
* HTTP methods
* Exception types
* Authentication-related issues
* Database-related issues
* Timeout indicators
* File names mentioned in logs

### Structured Troubleshooting Output

The system returns structured analysis including:

* Summary
* Category
* Severity
* Probable root causes
* Recommended debugging steps
* Extracted signals

### Additional Capabilities

* Simple web interface for manual testing
* Supports **heuristic analysis** and **optional LLM-based analysis**
* REST API endpoints for **single-log** and **batch analysis**

---

## Architecture

```
User Browser
     │
     ▼
Nginx (Reverse Proxy)
     │
     ▼
Gunicorn (WSGI Server)
     │
     ▼
Flask Application
     │
     ├── Heuristic Log Analysis
     └── Optional OpenAI API Analysis
```

---

## Project Structure

```
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

## Installation

Clone the repository:

```
git clone https://github.com/Ellibrinker/ai_troubleshooting_agent.git
cd ai_troubleshooting_agent
```

Create a virtual environment:

```
python -m venv .venv
```

Activate the environment.

### Windows

```
.venv\Scripts\activate
```

### macOS / Linux

```
source .venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```
OPENAI_API_KEY=your_api_key_here
USE_OPENAI=false
FLASK_ENV=development
```

### Notes

* Set `USE_OPENAI=true` to enable OpenAI-based analysis
* If OpenAI is not enabled or fails, the app falls back to heuristic analysis
* The `.env` file is **not committed to Git** for security reasons

---

## Running the Application

Start the Flask server:

```
python app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

---

## API Endpoints

### Health Check

**GET /health**

Example response:

```
{
  "status": "ok"
}
```

---

### Analyze a Single Log

**POST /analyze**

Example request:

```
{
  "log_text": "POST /api/orders returned 500. KeyError user_id in order_service.py",
  "source": "orders-service",
  "environment": "production",
  "timestamp": "2026-03-13T10:20:00Z"
}
```

Example response:

```
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

### Analyze Multiple Logs

**POST /analyze/batch**

Example request:

```
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

```
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

## Deployment

The application is deployed on **AWS EC2** with a production-style setup:

* **Nginx** as a reverse proxy
* **Gunicorn** as the WSGI server
* **Flask** as the backend application
* **systemd** used for process management

This project demonstrates a production-style deployment of a Python backend service on AWS using **Nginx**, **Gunicorn**, and **systemd for process management**.

---

## Technologies Used

* Python
* Flask
* JavaScript
* HTML
* CSS
* OpenAI API
* Gunicorn
* Nginx
* AWS EC2

---

## Future Improvements

* Deploy the service with Docker
* Add support for structured JSON logs
* Improve categorization and severity scoring
* Add authentication for public API access
* Integrate with real observability or logging systems

---

## Author

**Elli Brinker**
