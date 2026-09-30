from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="voter")
    has_voted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    votes = db.relationship("Vote", backref="voter", lazy=True)


class Election(db.Model):
    __tablename__ = "elections"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="draft", nullable=False)

    candidates = db.relationship("Candidate", backref="election", lazy=True)
    votes = db.relationship("Vote", backref="election", lazy=True)


class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    party = db.Column(db.String(120), nullable=False)
    symbol = db.Column(db.String(120), nullable=True)
    election_id = db.Column(db.Integer, db.ForeignKey("elections.id"), nullable=False)


class Vote(db.Model):
    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True)
    election_id = db.Column(db.Integer, db.ForeignKey("elections.id"), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    encrypted_vote = db.Column(db.Text, nullable=False)
    nonce = db.Column(db.String(255), nullable=False)
    authentication_tag = db.Column(db.String(255), nullable=False)
    signature = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
