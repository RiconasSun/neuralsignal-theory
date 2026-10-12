"""Authenticated byte envelopes; no key/plaintext is part of a public envelope."""
import json
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def aad(context):
    if not isinstance(context, dict) or not context:
        raise ValueError('INVALID_AUTHENTICATED_CONTEXT')
    return json.dumps(context, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def seal(key, plaintext, context):
    if not isinstance(key, bytes) or len(key) != 32 or not isinstance(plaintext, bytes):
        raise ValueError('INVALID_KEY_OR_PAYLOAD')
    nonce = os.urandom(12)
    return b'P12GCM1\0' + nonce + AESGCM(key).encrypt(nonce, plaintext, aad(context))


def unseal(key, envelope, context):
    if not isinstance(key, bytes) or len(key) != 32 or not isinstance(envelope, bytes):
        raise ValueError('INVALID_KEY_OR_ENVELOPE')
    if len(envelope) < 36 or envelope[:8] != b'P12GCM1\0':
        raise ValueError('INVALID_ENVELOPE_FRAMING')
    return AESGCM(key).decrypt(envelope[8:20], envelope[20:], aad(context))
