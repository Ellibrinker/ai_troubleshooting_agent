# AI Security Log Analysis & Troubleshooting Agent

## Web-based debugging assistant for backend and security logs

AI Security Log Analysis & Troubleshooting Agent is a lightweight debugging assistant for backend systems and security-related events.  
The tool analyzes application logs or error messages and returns structured troubleshooting insights, including detected signals, probable root causes, and recommended debugging steps.

Built with **Python** and **Flask**, the project exposes REST API endpoints for programmatic log analysis and includes a simple browser-based UI for testing.

---

## Live Demo

👉 **[Live Demo](http://13.49.66.245)**

---

## Features

### Log Analysis

- Analyze application logs and error messages

### Signal Detection

The tool automatically detects troubleshooting signals such as:

- HTTP status codes  
- API endpoints  
- HTTP methods  
- exception types  
- authentication-related issues  
- database-related issues  
- timeout indicators  
- file names mentioned in logs  

### Security Detection

The tool also detects common security-related signals such as:

- brute force login attempts  
- SQL injection patterns  
- suspicious privileged access  
- root login anomalies  
- authentication abuse indicators  

### Structured Troubleshooting Output

The system returns structured analysis including:

- summary  
- category  
- severity  
- probable root causes  
- debugging steps  
- extracted signals  

### Additional Capabilities

- Simple web interface for manual testing  
- Supports both **heuristic analysis** and **optional LLM-based analysis**  
- REST API endpoints for **single-log** and **batch analysis**  
- Demo examples for both backend failures and security-related incidents  

---

## Architecture

```text
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

### Windows

```bash
.venv\Scripts\activate
```

### macOS / Linux

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

- Set `USE_OPENAI=true` to enable OpenAI-based analysis  
- If OpenAI is not enabled or fails, the app falls back to heuristic analysis  
- The `.env` file is **not committed to Git** for security reasons  

---

# Running the Application

Start the Flask server:

```bash
python app.py
```

Then open your browser and go to:

```text
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
  "summary": "Likely issue involves backend request handling, validation, dependency behavior, environment-specific configuration, or a potential security-related event.",
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
    "contains_traceback": false,
    "contains_bruteforce": false,
    "contains_sql_injection": false,
    "contains_privilege_escalation": false
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

## Analyze Security-Related Logs

**POST /analyze**

Example request:

```json
{
  "log_text": "Failed login attempt for user admin from IP 185.23.44.12. Authentication failed. Too many login attempts detected.",
  "source": "auth-service",
  "environment": "production",
  "timestamp": "2026-03-13T10:20:00Z"
}
```

Example response:

```json
{
  "mode": "heuristic",
  "summary": "Likely issue involves backend request handling, validation, dependency behavior, environment-specific configuration, or a potential security-related event.",
  "category": "security",
  "severity": "high",
  "source": "auth-service",
  "environment": "production",
  "timestamp": "2026-03-13T10:20:00Z",
  "signals": {
    "status_codes": [],
    "endpoints": [],
    "exception_type": null,
    "http_method": null,
    "file_name": null,
    "contains_timeout": false,
    "contains_auth": true,
    "contains_db": false,
    "contains_null_or_missing": false,
    "contains_traceback": false,
    "contains_bruteforce": true,
    "contains_sql_injection": false,
    "contains_privilege_escalation": false
  },
  "probable_causes": [
    "Multiple failed authentication attempts detected, possibly indicating a brute force attack.",
    "Authentication or authorization failure, possibly due to an invalid token, expired credentials, or insufficient scope."
  ],
  "debugging_steps": [
    "Check authentication logs, identify suspicious IP addresses, and enforce rate limiting or temporary account lockouts.",
    "Validate tokens, permissions, request headers, and any auth middleware or connector scopes."
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
      "log_text": "GET /login?username=admin' OR 1=1-- returned 500 SQL syntax error in auth_handler.py",
      "source": "web-gateway",
      "environment": "production"
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
      "summary": "Likely issue involves backend request handling, validation, dependency behavior, environment-specific configuration, or a potential security-related event.",
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
        "contains_traceback": false,
        "contains_bruteforce": false,
        "contains_sql_injection": false,
        "contains_privilege_escalation": false
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

# Deployment

The application is deployed on **AWS EC2** with a production-style setup:

- **Nginx** as a reverse proxy  
- **Gunicorn** as the WSGI server  
- **Flask** as the backend application  
- **systemd** used for process management  

This project demonstrates a production-style deployment of a Python backend service on AWS using **Nginx**, **Gunicorn**, and **systemd**.

---

# Technologies Used

- Python  
- Flask  
- JavaScript  
- HTML  
- CSS  
- OpenAI API  
- Gunicorn  
- Nginx  
- AWS EC2  

---

# Future Improvements

- Deploy the service with Docker  
- Add support for structured JSON logs  
- Improve categorization and severity scoring  
- Add authentication for public API access  
- Integrate with real observability or logging systems  
- Expand security detection coverage for additional attack patterns  

---

# Author

**Elli Brinker**
