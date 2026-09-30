import base64
import os

from services.aes_service import decrypt_vote_data, derive_key_from_seed, encrypt_vote_data, generate_vote_master_key
from services.dh_service import derive_aes_key, derive_shared_secret, generate_dh_keypair
from services.signature_service import sign_vote_payload, verify_vote_payload


def build_vote_security_context():
    """Create a demo DH security context for the vote transaction."""
    client_private, client_public = generate_dh_keypair()
    server_private, server_public = generate_dh_keypair()
    shared_secret = derive_shared_secret(server_private, client_public)
    aes_key = derive_aes_key(shared_secret)
    return {
        "client_private": client_private,
        "client_public": client_public,
        "server_private": server_private,
        "server_public": server_public,
        "shared_secret": shared_secret,
        "aes_key": aes_key,
        "security_note": "Server and voter establish a shared secret conceptually before vote encryption.",
    }


def create_secure_vote(voter_id: int, election_id: int, candidate_id: int):
    """Encrypt and sign the vote, demonstrating the secure workflow."""
    security_context = build_vote_security_context()
    secure_nonce = os.urandom(12)
    payload = {
        "voter_id": voter_id,
        "election_id": election_id,
        "candidate_id": candidate_id,
        "vote_nonce": secure_nonce.hex(),
    }

    # In this educational demo, the vote is encrypted with a derived server-side key
    # while the DH values are retained as proof of the secure key-exchange concept.
    master_key = generate_vote_master_key()
    vote_key = derive_key_from_seed(master_key, secure_nonce)
    encrypted_vote, nonce, auth_tag = encrypt_vote_data(payload, vote_key, nonce=secure_nonce)
    signature = sign_vote_payload(voter_id, election_id, candidate_id, nonce, encrypted_vote)

    return {
        "payload": payload,
        "encrypted_vote": encrypted_vote,
        "nonce": nonce,
        "authentication_tag": auth_tag,
        "signature": signature,
        "security_context": security_context,
        "vote_key": vote_key,
    }


def verify_secure_vote(voter_id: int, election_id: int, candidate_id: int, encrypted_vote: str, nonce: str, authentication_tag: str, signature: str):
    """Verify the vote signature before acceptance."""
    master_key = generate_vote_master_key()
    vote_key = derive_key_from_seed(master_key, base64.b64decode(nonce))
    try:
        decrypted = decrypt_vote_data(encrypted_vote, nonce, authentication_tag, vote_key)
    except Exception:
        return False, None

    signed_candidate_id = decrypted.get("candidate_id")
    if signed_candidate_id != candidate_id:
        return False, None

    valid = verify_vote_payload(voter_id, election_id, candidate_id, nonce, encrypted_vote, signature)
    return valid, decrypted


def count_results_for_election(election_id: int):
    """Decrypt and count each stored vote for the election."""
    from models.models import Vote, Candidate

    votes = Vote.query.filter_by(election_id=election_id).all()
    counts = {}
    for vote in votes:
        key = derive_key_from_seed(generate_vote_master_key(), base64.b64decode(vote.nonce))
        decrypted = decrypt_vote_data(vote.encrypted_vote, vote.nonce, vote.authentication_tag, key)
        candidate_id = decrypted.get("candidate_id")
        counts[candidate_id] = counts.get(candidate_id, 0) + 1

    candidate_rows = Candidate.query.filter_by(election_id=election_id).all()
    result_rows = []
    for candidate in candidate_rows:
        result_rows.append({
            "candidate": candidate,
            "count": counts.get(candidate.id, 0),
        })
    return result_rows
