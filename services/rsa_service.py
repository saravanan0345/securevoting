import base64
import os
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key

KEYS_DIR = (
    Path("/tmp/secure-voting-keys")
    if os.getenv("VERCEL")
    else Path(__file__).resolve().parent.parent / "keys"
)
PRIVATE_KEY_PATH = KEYS_DIR / "server_private_key.pem"
PUBLIC_KEY_PATH = KEYS_DIR / "server_public_key.pem"


def ensure_server_keypair():
    """Create RSA keypair once for server authentication and signature verification."""
    KEYS_DIR.mkdir(exist_ok=True)
    if PRIVATE_KEY_PATH.exists() and PUBLIC_KEY_PATH.exists():
        return load_server_keys()

    private_key = generate_private_key(public_exponent=65537, key_size=2048)
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    PRIVATE_KEY_PATH.write_bytes(private_bytes)
    PUBLIC_KEY_PATH.write_bytes(public_bytes)
    return load_server_keys()


def load_server_keys():
    private_key = serialization.load_pem_private_key(PRIVATE_KEY_PATH.read_bytes(), password=None)
    public_key = serialization.load_pem_public_key(PUBLIC_KEY_PATH.read_bytes())
    return private_key, public_key


def sign_data(data: bytes) -> str:
    private_key, _ = ensure_server_keypair()
    signature = private_key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("utf-8")


def verify_signature(data: bytes, signature_b64: str) -> bool:
    _, public_key = ensure_server_keypair()
    try:
        public_key.verify(
            base64.b64decode(signature_b64),
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False


def get_public_key_pem() -> bytes:
    _, public_key = ensure_server_keypair()
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
