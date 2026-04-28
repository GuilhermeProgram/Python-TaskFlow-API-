"""
auth.py - Autenticação JWT (sem dependências externas)
"""

import hmac
import hashlib
import base64
import json
import time
from functools import wraps
from flask import request, jsonify


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


def _b64_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + '=' * padding)


def generate_token(user_id: int, secret: str, expires_in: int = 86400) -> str:
    """Gera token JWT simples (HS256)."""
    header = _b64_encode(json.dumps({'alg': 'HS256', 'typ': 'JWT'}).encode())
    payload = _b64_encode(json.dumps({
        'user_id': user_id,
        'exp': int(time.time()) + expires_in,
        'iat': int(time.time())
    }).encode())

    signature_input = f"{header}.{payload}".encode()
    sig = hmac.new(secret.encode(), signature_input, hashlib.sha256).digest()
    signature = _b64_encode(sig)

    return f"{header}.{payload}.{signature}"


def verify_token(token: str, secret: str):
    """Valida e decodifica o token. Retorna payload ou None."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None

        header, payload, signature = parts
        expected_sig_input = f"{header}.{payload}".encode()
        expected_sig = _b64_encode(
            hmac.new(secret.encode(), expected_sig_input, hashlib.sha256).digest()
        )

        if not hmac.compare_digest(signature, expected_sig):
            return None

        data = json.loads(_b64_decode(payload))
        if data.get('exp', 0) < time.time():
            return None  # token expirado

        return data
    except Exception:
        return None


def token_required(secret: str):
    """Decorator para proteger rotas com JWT."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Token não fornecido'}), 401

            token = auth_header.split(' ', 1)[1]
            payload = verify_token(token, secret)

            if not payload:
                return jsonify({'error': 'Token inválido ou expirado'}), 401

            return f(payload['user_id'], *args, **kwargs)
        return wrapper
    return decorator
