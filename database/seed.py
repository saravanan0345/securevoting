from datetime import datetime, timedelta, timezone

from werkzeug.security import generate_password_hash

from config import Config
from models.models import Candidate, Election, User, db


def seed_demo_data():
    admin = User.query.filter_by(role="admin").first()
    if admin is None:
        admin = User(
            voter_id=Config.ADMIN_USERNAME,
            name="System Administrator",
            email=Config.ADMIN_EMAIL,
            password_hash=generate_password_hash(Config.ADMIN_PASSWORD),
            role="admin",
            has_voted=False,
        )
        db.session.add(admin)
    else:
        admin.voter_id = Config.ADMIN_USERNAME
        admin.email = Config.ADMIN_EMAIL
        admin.password_hash = generate_password_hash(Config.ADMIN_PASSWORD)

    if User.query.filter_by(role="voter").first() or Election.query.first():
        db.session.commit()
        return

    voter1 = User(
        voter_id="DEMO001",
        name="Aisha Patel",
        email="aisha@example.com",
        password_hash=generate_password_hash("Password123!"),
        has_voted=False,
    )
    voter2 = User(
        voter_id="DEMO002",
        name="Daniel Moss",
        email="daniel@example.com",
        password_hash=generate_password_hash("Password123!"),
        has_voted=False,
    )
    voter3 = User(
        voter_id="DEMO003",
        name="Priya Singh",
        email="priya@example.com",
        password_hash=generate_password_hash("Password123!"),
        has_voted=False,
    )
    db.session.add_all([voter1, voter2, voter3])

    election = Election(
        name="Student Council Election 2026",
        description="Choose the next student council president for the academic year.",
        start_date=datetime.now(timezone.utc) - timedelta(days=3),
        end_date=datetime.now(timezone.utc) + timedelta(days=10),
        status="active",
    )
    db.session.add(election)
    db.session.flush()

    candidates = [
        Candidate(name="Alice Johnson", party="Blue Alliance", symbol="🔵", election_id=election.id),
        Candidate(name="Mark Lee", party="Green Future", symbol="🟢", election_id=election.id),
        Candidate(name="Priya Shah", party="Unity Party", symbol="🟣", election_id=election.id),
    ]
    db.session.add_all(candidates)
    db.session.commit()

    return {
        "admin": admin,
        "election": election,
        "voters": [voter1, voter2, voter3],
        "candidates": candidates,
    }
