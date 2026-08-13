"""SLA113 Operator Auth — lightweight auth server for the operator login gate.

The SLA113LoginGate in the frontend POSTs {handle, password} to /api/auth/login.
This server handles that without requiring the full MongoDB-backed backend.

Credentials come from env vars (with defaults for dev):
  SLA113_OPERATOR_HANDLE=admin
  SLA113_OPERATOR_PASSWORD=admin

Runs standalone on port 8001 (matching the prod backend port).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


OPERATOR_HANDLE = os.environ.get("SLA113_OPERATOR_HANDLE", "admin")
OPERATOR_PASSWORD = os.environ.get("SLA113_OPERATOR_PASSWORD", "admin")
SECRET = os.environ.get("SLA113_TOKEN_SECRET", "sla113-dev-secret-change-in-prod")


def make_token(handle: str) -> str:
    payload = json.dumps({
        "handle": handle,
        "iat": int(time.time()),
        "jti": uuid.uuid4().hex[:16],
    }, separators=(",", ":"))
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def verify_token(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        payload_raw, sig = parts
        expected = hmac.new(SECRET.encode(), payload_raw.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return json.loads(payload_raw)
    except (json.JSONDecodeError, ValueError):
        return None


class LoginRequest(BaseModel):
    handle: str
    password: str


class LoginResponse(BaseModel):
    token: str
    handle: str
    token_type: str = "bearer"


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "sla113-operator-auth"


app = FastAPI(title="SLA113 Operator Auth", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.post("/api/auth/login", response_model=LoginResponse)
async def operator_login(req: LoginRequest):
    if req.handle == OPERATOR_HANDLE and req.password == OPERATOR_PASSWORD:
        return LoginResponse(
            token=make_token(req.handle),
            handle=req.handle,
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/api/auth/verify")
async def verify(token_body: dict):
    token = token_body.get("token", "")
    payload = verify_token(token)
    if payload:
        return {"valid": True, "handle": payload["handle"]}
    return {"valid": False}
