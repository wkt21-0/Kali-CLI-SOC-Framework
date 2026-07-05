#!/usr/bin/env python3
"""
FastAPI ingestion server for endpoint agent events.

Security features:
- API key required in X-API-Key header (value comes from INGEST_API_KEY env var).
- Certificate verification expected at transport layer (HTTPS).
- Atomic writes to data/logs/endpoint.json to avoid partial writes.
- Basic Pydantic model for event validation (extra fields allowed).
"""
from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Extra
from typing import List, Union, Optional, Any
from pathlib import Path
import os
import hmac
import json
import logging
import tempfile

LOG_DIR = Path("data/logs")
ENDPOINT_FILE = LOG_DIR / "endpoint.json"
API_KEY_ENV = "INGEST_API_KEY"

app = FastAPI(title="SOC Ingest API", version="0.1.0")
logger = logging.getLogger("uvicorn.error")


class Event(BaseModel, extra=Extra.allow):
    # allow arbitrary fields — keep a few recommended fields typed
    type: Optional[str] = None
    timestamp: Optional[str] = None
    pid: Optional[int] = None
    name: Optional[str] = None
    cmdline: Optional[Any] = None


def _get_expected_api_key() -> str:
    val = os.getenv(API_KEY_ENV)
    if not val:
        # In production, fail early. In lab mode you may set this env var.
        logger.warning("INGEST_API_KEY not set — server will reject all requests.")
        return ""
    return val


def _check_api_key(provided: str) -> bool:
    expected = _get_expected_api_key()
    if not expected:
        return False
    # constant-time compare
    try:
        return hmac.compare_digest(provided.strip(), expected.strip())
    except Exception:
        return False


def _atomic_append_json_list(path: Path, items: List[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if path.exists():
        try:
            existing = json.loads(path.read_text())
            if not isinstance(existing, list):
                existing = []
        except Exception:
            existing = []

    combined = existing + items
    # atomic write
    with tempfile.NamedTemporaryFile("w", delete=False, dir=str(path.parent)) as tf:
        tf.write(json.dumps(combined, indent=2))
        temp_name = tf.name
    Path(temp_name).replace(path)


@app.post("/ingest")
async def ingest(events: Union[Event, List[Event]], x_api_key: Optional[str] = Header(None)):
    if not x_api_key or not _check_api_key(x_api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # normalize to list of dicts
    if isinstance(events, list):
        payload = [e.dict() for e in events]
    else:
        payload = [events.dict()]

    # basic validation: reject empty payloads
    if not payload:
        raise HTTPException(status_code=400, detail="Empty payload")

    try:
        _atomic_append_json_list(ENDPOINT_FILE, payload)
        logger.info("Ingested %d events", len(payload))
    except Exception as e:
        logger.exception("Failed to persist events: %s", e)
        raise HTTPException(status_code=500, detail="Failed to persist events")
    return {"received": len(payload)}
