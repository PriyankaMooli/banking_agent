"""Sign and verify the authenticated principal passed to the backend."""

import base64
import hashlib
import hmac
import json
import os
import time


def _secret() -> bytes:
    secret = os.environ.get("AUTHZ_SHARED_SECRET", "")
    if not secret:
        raise ValueError("AUTHZ_SHARED_SECRET must be configured")
    return secret.encode("utf-8")


def _encode(payload: bytes) -> str:
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def sign_principal(subject: str, tier: str) -> str:
    if not subject or tier not in {"customer", "privileged"}:
        raise ValueError("Invalid principal")
    payload = json.dumps(
        {"subject": subject, "tier": tier, "exp": int(time.time()) + 60},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    encoded = _encode(payload)
    signature = hmac.new(_secret(), encoded.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded}.{_encode(signature)}"


def verify_principal(token: str) -> dict[str, str]:
    try:
        encoded, supplied_signature = token.split(".", 1)
        expected_signature = _encode(
            hmac.new(_secret(), encoded.encode("ascii"), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(supplied_signature, expected_signature):
            raise ValueError("Invalid principal signature")
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        principal = json.loads(payload)
        subject, tier, expires_at = (
            principal["subject"],
            principal["tier"],
            principal["exp"],
        )
        if (
            not isinstance(subject, str)
            or not subject
            or tier not in {"customer", "privileged"}
            or not isinstance(expires_at, int)
            or expires_at <= time.time()
        ):
            raise ValueError("Invalid principal")
        return {"subject": subject, "tier": tier}
    except (AttributeError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid principal") from exc
