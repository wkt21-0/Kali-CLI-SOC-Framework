#!/usr/bin/env python3
"""
Secure agent transport for sending events to the SOC ingest server.

Configuration via environment variables:
- SOC_INGEST_URL (e.g. https://soc.example.com:5514/ingest)
- SOC_API_KEY      (the API key to put in X-API-Key header)
- SOC_VERIFY_CERT  (optional; path to CA bundle or "false" to skip verification - NOT recommended)
"""
import os
import json
import requests
from requests.adapters import HTTPAdapter, Retry

DEFAULT_TIMEOUT = 5  # seconds

SOC_INGEST_URL_ENV = "SOC_INGEST_URL"
SOC_API_KEY_ENV = "SOC_API_KEY"
SOC_VERIFY_CERT_ENV = "SOC_VERIFY_CERT"


def _build_session():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s


def send_event(event: dict):
    url = os.getenv(SOC_INGEST_URL_ENV)
    api_key = os.getenv(SOC_API_KEY_ENV)
    verify = os.getenv(SOC_VERIFY_CERT_ENV, "true")

    if not url or not api_key:
        raise RuntimeError("SOC_INGEST_URL and SOC_API_KEY must be set in environment")

    # allow explicit 'false' (case-insensitive) to disable cert verification (use only in lab)
    if verify.lower() in ("false", "0", "no"):
        verify_val = False
    else:
        # could be 'true' or a path to a CA bundle
        verify_val = True if verify.lower() in ("true", "1", "yes") else verify

    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }

    s = _build_session()
    try:
        resp = s.post(url, headers=headers, data=json.dumps(event), timeout=DEFAULT_TIMEOUT, verify=verify_val)
        resp.raise_for_status()
        return resp
    except requests.RequestException as e:
        # in production consider exponential backoff + persistence on failure
        print(f"[Agent] Failed to send event: {e}")
        raise
