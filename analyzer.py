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

    return {
        "status_codes": list(dict.fromkeys(status_codes)),
        "endpoints": list(dict.fromkeys(endpoints))[:5],
        "exception_type": exception_match.group(1) if exception_match else None,
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
    }


def _heuristic_analysis(log_text: str) -> dict[str, Any]:
    signals = _extract_signals(log_text)
    probable_causes: list[str] = []
    debugging_steps: list[str] = []

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
            "Authentication or authorization failure, possibly due to invalid token or insufficient scope."
        )
        debugging_steps.append(
            "Validate token, permissions, and request headers. Check auth middleware or connector scopes."
        )

    if "404" in signals["status_codes"]:
        probable_causes.append(
            "Invalid route, missing resource, or incorrect identifier passed to the request."
        )
        debugging_steps.append(
            "Verify endpoint path, resource ID, and whether the entity exists in the expected environment."
        )

    if signals["contains_timeout"]:
        probable_causes.append(
            "Upstream dependency, slow query, or network-related timeout."
        )
        debugging_steps.append(
            "Check external service latency, DB query time, and retry/timeout configuration."
        )

    if signals["contains_db"]:
        probable_causes.append(
            "Database constraint, schema mismatch, or invalid data flow."
        )
        debugging_steps.append(
            "Review recent inserts/updates, validate schema assumptions, and inspect SQL/database errors."
        )

    if signals["contains_null_or_missing"]:
        probable_causes.append(
            "Missing or malformed input data leading to null/undefined access."
        )
        debugging_steps.append(
            "Validate request payload fields and add guards for missing values before access."
        )

    if signals["exception_type"]:
        probable_causes.append(
            f"Application raised {signals['exception_type']}, indicating a code-path or data handling issue."
        )
        debugging_steps.append(
            f"Search for the exact {signals['exception_type']} location in code and inspect the triggering input."
        )

    if not probable_causes:
        probable_causes.append(
            "Insufficient signal for a precise diagnosis; issue may depend on request context or environment configuration."
        )
        debugging_steps.extend(
            [
                "Collect the full request payload, response status, and timestamp.",
                "Compare failing flow against a known successful request.",
                "Check recent configuration or deployment changes.",
            ]
        )

    summary = (
        "Likely issue involves backend handling, request validation, or "
        "environment-specific behavior."
    )

    return {
        "mode": "heuristic",
        "summary": summary,
        "signals": signals,
        "probable_causes": probable_causes[:4],
        "debugging_steps": debugging_steps[:5],
    }


def _openai_analysis(log_text: str) -> dict[str, Any]:
    if not OPENAI_API_KEY:
        return _heuristic_analysis(log_text)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = f"""
You are a technical troubleshooting assistant for web applications.
Analyze the following log or error text and return:
1. A short summary
2. Up to 4 probable root causes
3. Up to 5 debugging steps

Error/Log:
{log_text}
"""

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        text = response.output_text.strip()

        return {
            "mode": "openai",
            "summary": text,
            "signals": _extract_signals(log_text),
            "probable_causes": [],
            "debugging_steps": [],
        }
    except Exception as exc:
        fallback = _heuristic_analysis(log_text)
        fallback["mode"] = "heuristic_fallback"
        fallback["fallback_reason"] = str(exc)
        return fallback


def analyze_log(log_text: str) -> dict[str, Any]:
    if USE_OPENAI:
        return _openai_analysis(log_text)
    return _heuristic_analysis(log_text)