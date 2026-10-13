import secrets

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


RESERVED_KEY = bytes(32)

HKDF_INFO = b"SIMServe-v1"
HKDF_SALT = b""

AES_KEY_SIZE = 32
GCM_NONCE_SIZE = 12
GCM_TAG_SIZE = 16
CHALLENGE_SIZE = 32


def derive_peer_key(
    private_key: X25519PrivateKey,
    peer_public_key: X25519PublicKey,
) -> bytes:
    shared_secret = private_key.exchange(peer_public_key)

    return HKDF(
        algorithm=hashes.SHA256(),
        length=AES_KEY_SIZE,
        salt=HKDF_SALT,
        info=HKDF_INFO,
    ).derive(shared_secret)


def encrypt_payload(
    key: bytes,
    payload: bytes,
    aad: bytes,
) -> bytes:
    nonce = secrets.token_bytes(GCM_NONCE_SIZE)

    ciphertext = AESGCM(key).encrypt(
        nonce,
        payload,
        aad,
    )

    return nonce + ciphertext


def decrypt_payload(
    key: bytes,
    payload: bytes,
    aad: bytes,
) -> bytes:
    if len(payload) < GCM_NONCE_SIZE + GCM_TAG_SIZE:
        raise ValueError("Invalid challenge payload")

    nonce = payload[:GCM_NONCE_SIZE]
    ciphertext = payload[GCM_NONCE_SIZE:]

    return AESGCM(key).decrypt(
        nonce,
        ciphertext,
        aad,
    )
