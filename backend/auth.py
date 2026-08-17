from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import hashlib
import hmac
import json
from fastapi import HTTPException, Request

@dataclass(frozen=True)
class Identity:
    subject: str
    scopes: tuple[str, ...] = ()

def _decode_part(value: str) -> dict:
    padding = '=' * (-len(value) % 4)
    return json.loads(base64.urlsafe_b64decode(value + padding))

def verify_bearer(request: Request, token_secret: str | None, required: bool) -> Identity:
    header = request.headers.get('authorization', '')
    if not header:
        if required:
            raise HTTPException(status_code=401, detail='Bearer token required')
        return Identity('local-dev')
    if not header.lower().startswith('bearer '):
        raise HTTPException(status_code=401, detail='Bearer token required')
    if not token_secret:
        raise HTTPException(status_code=503, detail='JWT secret is not configured')
    token = header[7:].strip()
    parts = token.split('.')
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail='Malformed JWT')
    encoded_header, encoded_payload, signature = parts
    expected = base64.urlsafe_b64encode(hmac.new(token_secret.encode(), f'{encoded_header}.{encoded_payload}'.encode(), hashlib.sha256).digest()).decode().rstrip('=')
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail='Invalid JWT signature')
    payload = _decode_part(encoded_payload)
    if payload.get('exp') and datetime.fromtimestamp(payload['exp'], tz=timezone.utc) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail='JWT expired')
    subject = payload.get('sub')
    if not subject:
        raise HTTPException(status_code=401, detail='JWT subject missing')
    scopes = tuple(payload.get('scope', '').split()) if isinstance(payload.get('scope'), str) else tuple(payload.get('scopes', []))
    return Identity(subject, scopes)

def current_identity(request: Request) -> Identity:
    return verify_bearer(request, getattr(request.app.state, 'jwt_secret', None), getattr(request.app.state, 'auth_required', False))
