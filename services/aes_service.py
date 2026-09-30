import base64
import hashlib
import json
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

MASTER_KEY_PATH = Path(__file__).resolve().parent.parent / "keys" / "vote_master_key.bin"


def generate_vote_master_key() -> bytes:
    configured_key = os.getenv("VOTING_MASTER_KEY")
    if os.getenv("VERCEL"):
        if not configured_key:
            raise RuntimeError("VOTING_MASTER_KEY must be configured on Vercel.")
        return hashlib.sha256(configured_key.encode("utf-8")).digest()

    MASTER_KEY_PATH.parent.mkdir(exist_ok=True)
    if MASTER_KEY_PATH.exists():
        return MASTER_KEY_PATH.read_bytes()
    key = AESGCM.generate_key(bit_length=256)
    MASTER_KEY_PATH.write_bytes(key)
    return key


def derive_key_from_seed(seed: bytes, nonce: bytes) -> bytes:
    kdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=nonce,
        info=b"secure-voting-aes",
    )
    return kdf.derive(seed)


def encrypt_vote_data(payload: dict, key: bytes = None, nonce: bytes = None) -> tuple[str, str, str]:
    if key is None:
        key = generate_vote_master_key()
    if nonce is None:
        nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    plaintext = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    encrypted_vote = base64.b64encode(ciphertext[:-16]).decode("utf-8")
    tag = base64.b64encode(ciphertext[-16:]).decode("utf-8")
    return encrypted_vote, base64.b64encode(nonce).decode("utf-8"), tag


def decrypt_vote_data(encrypted_vote: str, nonce: str, authentication_tag: str, key: bytes) -> dict:
    aesgcm = AESGCM(key)
    ciphertext = base64.b64decode(encrypted_vote) + base64.b64decode(authentication_tag)
    plaintext = aesgcm.decrypt(base64.b64decode(nonce), ciphertext, None)
    return json.loads(plaintext.decode("utf-8"))
