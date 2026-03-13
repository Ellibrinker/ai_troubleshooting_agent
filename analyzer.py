import json
import os
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()

USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


def _extract_signals(log_text: str) -> dict[str, Any]:
    text = log_text.lower()

    status_codes = re.findall(r"\b(4\d{2}|5\d{2})\b", log_text)
    endpoints = re.findall(r"(\/[A-Za-z0-9_\-\/]+)", log_text)
    exception_match = re.search(
        r"(KeyError|ValueError|TypeError|AttributeError|TimeoutError|ConnectionError|PermissionError|IndexError|AuthenticationError|AuthorizationError)",
        log_text,
    )
    method_match = re.search(r"\b(GET|POST|PUT|DELETE|PATCH)\b", log_text)
    file_match = re.search(r"([A-Za-z0-9_\-]+\.py)", log_text)

    contains_bruteforce = any(
        token in text
        for token in [
            "failed login",
            "multiple failed login",
            "authentication failed",
            "invalid password",
            "too many login attempts",
            "login failed",
        ]
    )

    contains_sql_injection = any(
        token in text
        for token in [
            "or 1=1",
            "' or '1'='1",
            "'--",
            "union select",
            "sql syntax error",
            "drop table",
        ]
    )

    contains_privilege_escalation = any(
        token in text
        for token in [
            "sudo",
            "root login",
            "privilege escalation",
            "admin access granted",
            "elevated privileges",
            "unauthorized admin access",
        ]
    )

    return {
        "status_codes": list(dict.fromkeys(status_codes)),
        "endpoints": list(dict.fromkeys(endpoints))[:5],
        "exception_type": exception_match.group(1) if exception_match else None,
        "http_method": method_match.group(1) if method_match else None,
        "file_name": file_match.group(1) if file_match else None,
        "contains_timeout": "timeout" in text or "timed out" in text,
        "contains_auth": any(
            token in text
            for token in [
                "unauthorized",
                "forbidden",
                "token",
                "oauth",
                "authentication",
                "authorization",
                "scope",
                "permission",
            ]
        ),
        "contains_db": any(
            token in text
            for token in [
                "sql",
                "mysql",
                "database",
                "db",
                "constraint",
                "foreign key",
                "duplicate key",
                "unique violation",
            ]
        ),
        "contains_null_or_missing": any(
            token in text
            for token in [
                "none",
                "null",
                "missing",
                "not found",
                "keyerror",
                "undefined",
            ]
        ),
        "contains_traceback": "traceback" in text,
        "contains_bruteforce": contains_bruteforce,
        "contains_sql_injection": contains_sql_injection,
        "contains_privilege_escalation": contains_privilege_escalation,
    }


def _infer_category_and_severity(signals: dict[str, Any]) -> tuple[str, str]:
    if signals["contains_sql_injection"]:
        return "security", "high"

    if signals["contains_privilege_escalation"]:
        return "security", "high"

    if signals["contains_bruteforce"]:
        return "security", "high"

    if "500" in signals["status_codes"]:
        return "server", "high"

    if (
        "401" in signals["status_codes"]
        or "403" in signals["status_codes"]
        or signals["contains_auth"]
    ):
        return "authentication", "medium"

    if "404" in signals["status_codes"]:
        return "routing", "medium"

    if signals["contains_db"]:
        return "database", "high"

    if signals["contains_timeout"]:
        return "timeout", "medium"

    if signals["contains_null_or_missing"] or signals["exception_type"]:
        return "validation", "medium"

    return "general", "low"


def _heuristic_analysis(
    log_text: str,
    source: str = "unknown",
    environment: str = "unknown",
    timestamp: str | None = None,
) -> dict[str, Any]:
    signals = _extract_signals(log_text)
    probable_causes: list[str] = []
    debugging_steps: list[str] = []

    if signals["contains_bruteforce"]:
        probable_causes.append(
            "Multiple failed authentication attempts detected, possibly indicating a brute force attack."
        )
        debugging_steps.append(
            "Check authentication logs, identify suspicious IP addresses, and enforce rate limiting or temporary account lockouts."
        )

    if signals["contains_sql_injection"]:
        probable_causes.append(
            "Possible SQL injection attempt detected in request input or query parameters."
        )
        debugging_steps.append(
            "Review request parameters and ensure proper input sanitization and parameterized queries are used."
        )

    if signals["contains_privilege_escalation"]:
        probable_causes.append(
            "Suspicious privileged access or a possible privilege escalation attempt was detected."
        )
        debugging_steps.append(
            "Audit user permissions, review admin actions, and verify whether the privileged operation was authorized."
        )

    if "500" in signals["status_codes"]:
        probable_causes.append(
            "Unhandled server-side exception or missing validation in backend logic."
        )
        debugging_steps.append(
            "Inspect backend logs around the failing request and locate the full stack trace."
        )

    if (
        "401" in signals["status_codes"]
        or "403" in signals["status_codes"]
        or signals["contains_auth"]
    ):
        probable_causes.append(
            "Authentication or authorization failure, possibly due to an invalid token, expired credentials, or insufficient scope."
        )
        debugging_steps.append(
            "Validate tokens, permissions, request headers, and any auth middleware or connector scopes."
        )

    if "404" in signals["status_codes"]:
        probable_causes.append(
            "Invalid route, missing resource, or incorrect identifier passed to the request."
        )
        debugging_steps.append(
            "Verify the endpoint path, resource ID, and whether the requested entity exists in the expected environment."
        )

    if signals["contains_timeout"]:
        probable_causes.append(
            "Upstream dependency, slow database query, or network-related timeout."
        )
        debugging_steps.append(
            "Check external service latency, database query performance, and timeout or retry configuration."
        )

    if signals["contains_db"]:
        probable_causes.append(
            "Database constraint violation, schema mismatch, or invalid data flow."
        )
        debugging_steps.append(
            "Review recent inserts or updates, validate schema assumptions, and inspect the exact database error."
        )

    if signals["contains_null_or_missing"]:
        probable_causes.append(
            "Missing or malformed input data leading to null, undefined, or missing-key access."
        )
        debugging_steps.append(
            "Validate request payload fields and add guards before accessing optional or missing values."
        )

    if signals["exception_type"]:
        probable_causes.append(
            f"Application raised {signals['exception_type']}, indicating a code-path or data-handling issue."
        )
        debugging_steps.append(
            f"Search for the exact {signals['exception_type']} location in code and inspect the triggering input."
        )

    if not probable_causes:
        probable_causes.append(
            "Insufficient signal for a precise diagnosis; the issue may depend on request context or environment-specific configuration."
        )
        debugging_steps.extend(
            [
                "Collect the full request payload, response status, and timestamp.",
                "Compare the failing flow against a known successful request.",
                "Review recent deployment or configuration changes.",
            ]
        )

    category, severity = _infer_category_and_severity(signals)

    summary = (
        "Likely issue involves backend request handling, validation, dependency behavior, "
        "environment-specific configuration, or a potential security-related event."
    )

    return {
        "mode": "heuristic",
        "summary": summary,
        "category": category,
        "severity": severity,
        "source": source,
        "environment": environment,
        "timestamp": timestamp,
        "signals": signals,
        "probable_causes": probable_causes[:4],
        "debugging_steps": debugging_steps[:5],
    }


def _openai_analysis(
    log_text: str,
    source: str = "unknown",
    environment: str = "unknown",
    timestamp: str | None = None,
) -> dict[str, Any]:
    if not OPENAI_API_KEY:
        fallback = _heuristic_analysis(log_text, source, environment, timestamp)
        fallback["mode"] = "heuristic_fallback"
        fallback["fallback_reason"] = "OPENAI_API_KEY is missing"
        return fallback

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
You are a technical troubleshooting assistant for web applications and security-related logs.

Analyze the following log and return valid JSON only with this exact structure:
{{
  "summary": "short summary",
  "probable_causes": ["cause 1", "cause 2"],
  "debugging_steps": ["step 1", "step 2"],
  "category": "security | authentication | database | server | timeout | routing | validation | general",
  "severity": "low | medium | high"
}}

Consider both backend failures and possible security issues such as brute force attempts,
SQL injection, suspicious privileged access, authentication abuse, or abnormal access patterns.

Log:
{log_text}
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        raw_text = response.output_text.strip()
        parsed = json.loads(raw_text)

        return {
            "mode": "openai",
            "summary": parsed.get("summary", "Analysis generated successfully."),
            "category": parsed.get("category", "general"),
            "severity": parsed.get("severity", "medium"),
            "source": source,
            "environment": environment,
            "timestamp": timestamp,
            "signals": _extract_signals(log_text),
            "probable_causes": parsed.get("probable_causes", [])[:4],
            "debugging_steps": parsed.get("debugging_steps", [])[:5],
        }

    except Exception as exc:
        fallback = _heuristic_analysis(log_text, source, environment, timestamp)
        fallback["mode"] = "heuristic_fallback"
        fallback["fallback_reason"] = str(exc)
        return fallback


def analyze_log(
    log_text: str,
    source: str = "unknown",
    environment: str = "unknown",
    timestamp: str | None = None,
) -> dict[str, Any]:
    if USE_OPENAI:
        return _openai_analysis(log_text, source, environment, timestamp)

    return _heuristic_analysis(log_text, source, environment, timestamp)