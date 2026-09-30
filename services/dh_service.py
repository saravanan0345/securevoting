import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def generate_dh_keypair():
    """Generate a fresh ephemeral X25519 keypair for a vote session."""
    private_key = X25519PrivateKey.generate()
    return private_key, private_key.public_key()


def derive_shared_secret(private_key, peer_public_key):
    """Derive a shared secret from the private key and the peer public key."""
    return private_key.exchange(peer_public_key)


def derive_aes_key(shared_secret: bytes, salt: bytes = b"secure-voting-demo") -> bytes:
    """Use HKDF to derive a key suitable for AES-GCM encryption."""
    kdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=b"secure-voting-session",
    )
    return kdf.derive(shared_secret)


def encode_key(value: bytes) -> str:
    return base64.b64encode(value).decode("utf-8")
