# SPDX-License-Identifier: AGPL-3.0-or-later
"""DiscourseConnect wire format: base64(urlencoded query) + HMAC-SHA256 hex."""

import base64
import binascii
import hashlib
import hmac
import secrets
import time
from urllib.parse import parse_qsl, urlencode

NONCE_TTL_SECONDS = 600
SESSION_KEY = "discourse_connect_nonces"


class InvalidPayloadError(Exception):
    pass


def sign(secret: str, payload: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def build_request(secret: str, nonce: str, return_sso_url: str) -> tuple[str, str]:
    raw = urlencode({"nonce": nonce, "return_sso_url": return_sso_url})
    payload = base64.b64encode(raw.encode()).decode()
    return payload, sign(secret, payload)


def issue_nonce(session, state_id: str, now: float | None = None) -> str:
    nonce = secrets.token_hex(16)
    nonces = session.get(SESSION_KEY, {})
    nonces[nonce] = {"ts": now or time.time(), "state": state_id}
    session[SESSION_KEY] = nonces
    return nonce


def verify_response(secret: str, payload: str, sig: str, session, now=None):
    """Return (data, state_id) or raise InvalidPayloadError. Nonce is single-use."""
    if not payload or not sig:
        raise InvalidPayloadError("missing sso/sig")
    if not hmac.compare_digest(sign(secret, payload), sig):
        raise InvalidPayloadError("bad signature")
    try:
        raw = base64.b64decode(payload, validate=True).decode()
    except (binascii.Error, UnicodeDecodeError) as e:
        raise InvalidPayloadError("bad encoding") from e
    data = dict(parse_qsl(raw))
    nonces = session.get(SESSION_KEY, {})
    entry = nonces.pop(data.get("nonce", ""), None)
    session[SESSION_KEY] = nonces  # consumed even if expired
    if entry is None:
        raise InvalidPayloadError("unknown or reused nonce")
    if (now or time.time()) - entry["ts"] > NONCE_TTL_SECONDS:
        raise InvalidPayloadError("nonce expired")
    if not data.get("external_id"):
        raise InvalidPayloadError("missing external_id")
    return data, entry["state"]
