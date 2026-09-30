from services.rsa_service import sign_data, verify_signature


def sign_vote_payload(voter_id: int, election_id: int, candidate_id: int, nonce: str, encrypted_vote: str):
    data = f"{voter_id}:{election_id}:{candidate_id}:{nonce}:{encrypted_vote}".encode("utf-8")
    return sign_data(data)


def verify_vote_payload(voter_id: int, election_id: int, candidate_id: int, nonce: str, encrypted_vote: str, signature: str) -> bool:
    data = f"{voter_id}:{election_id}:{candidate_id}:{nonce}:{encrypted_vote}".encode("utf-8")
    return verify_signature(data, signature)
