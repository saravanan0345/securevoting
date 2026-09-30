from datetime import datetime, timedelta, timezone

import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app import create_app
from config import get_database_url
from models.models import Candidate, Election, User, Vote, db
from services.aes_service import generate_vote_master_key


@pytest.fixture()
def client():
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SESSION_COOKIE_SECURE": False,
    })
    with app.app_context():
        db.create_all()
        admin = User(
            voter_id="ADMIN-001",
            name="Admin",
            email="admin@test.local",
            password_hash=generate_password_hash("Admin@123"),
            role="admin",
        )
        voter = User(
            voter_id="DEMO001",
            name="Test Voter",
            email="voter@test.local",
            password_hash=generate_password_hash("Password123!"),
            role="voter",
        )
        election = Election(
            name="Demo Election",
            description="Election for testing",
            start_date=datetime.now(timezone.utc) - timedelta(days=1),
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
            status="active",
        )
        db.session.add_all([admin, voter, election])
        db.session.flush()
        c1 = Candidate(name="Candidate A", party="Party A", symbol="A", election_id=election.id)
        c2 = Candidate(name="Candidate B", party="Party B", symbol="B", election_id=election.id)
        db.session.add_all([c1, c2])
        db.session.commit()
    with app.test_client() as client:
        yield client


def test_successful_registration(client):
    response = client.post(
        "/register",
        data={
            "name": "Alice Example",
            "email": "alice@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration Successful" in response.data
    assert b"Go to Login" in response.data
    assert b"DEMO" in response.data


def test_public_assets_are_served(client):
    response = client.get("/css/style.css")
    assert response.status_code == 200
    assert b"min-height: 100vh" in response.data


def test_vercel_vote_key_is_stable(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("VOTING_MASTER_KEY", "test-deployment-master-secret")

    first_key = generate_vote_master_key()
    second_key = generate_vote_master_key()

    assert len(first_key) == 32
    assert first_key == second_key


def test_neon_storage_database_url_is_supported(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("STORAGE_DATABASE_URL", "postgresql://example:secret@host/db")

    assert get_database_url() == "postgresql+psycopg://example:secret@host/db"


def test_duplicate_registration(client):
    client.post(
        "/register",
        data={
            "name": "Alice Example",
            "email": "alice2@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
    )
    response = client.post(
        "/register",
        data={
            "name": "Alice Again",
            "email": "alice3@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration Successful" in response.data


def test_successful_login(client):
    response = client.post(
        "/login",
        data={
            "voter_id": "DEMO001",
            "password": "Password123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Login successful" in response.data


def test_invalid_login(client):
    response = client.post(
        "/login",
        data={
            "voter_id": "DEMO001",
            "password": "wrongpass",
        },
        follow_redirects=True,
    )
    assert b"invalid voter id or password" in response.data.lower()


def test_admin_login(client):
    response = client.post(
        "/admin/login",
        data={
            "username": "ADMIN-001",
            "password": "Admin@123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Admin login successful" in response.data


def test_vote_success_and_duplicate_vote(client):
    client.post("/login", data={"voter_id": "DEMO001", "password": "Password123!"}, follow_redirects=True)
    election = Election.query.first()
    candidate = Candidate.query.filter_by(election_id=election.id).first()
    vote_response = client.post(f"/vote/{election.id}", data={"candidate_id": candidate.id}, follow_redirects=True)
    assert b"securely recorded" in vote_response.data.lower()

    second_response = client.post(f"/vote/{election.id}", data={"candidate_id": candidate.id}, follow_redirects=True)
    assert b"already cast your vote" in second_response.data.lower()


def test_result_calculation(client):
    client.post("/login", data={"voter_id": "DEMO001", "password": "Password123!"}, follow_redirects=True)
    election = Election.query.first()
    candidate = Candidate.query.filter_by(election_id=election.id).first()
    client.post(f"/vote/{election.id}", data={"candidate_id": candidate.id}, follow_redirects=True)

    with client.session_transaction() as sess:
        sess.clear()
        sess["admin_id"] = 1
        sess["role"] = "admin"

    response = client.get("/admin/results", follow_redirects=True)
    assert response.status_code == 200
    assert b"Election Results" in response.data


def test_password_hash_validation(client):
    with client.application.app_context():
        user = User.query.filter_by(voter_id="DEMO001").first()
    assert check_password_hash(user.password_hash, "Password123!") is True


def test_election_not_active_scenario(client):
    client.post("/login", data={"voter_id": "DEMO001", "password": "Password123!"}, follow_redirects=True)
    election = Election.query.first()
    election.status = "closed"
    db.session.commit()
    response = client.post(f"/vote/{election.id}", data={"candidate_id": 1}, follow_redirects=True)
    assert b"not active" in response.data.lower()
