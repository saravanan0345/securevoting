from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from models.models import Candidate, Election, User, Vote, db
from services.voting_service import count_results_for_election, create_secure_vote, verify_secure_vote


auth_bp = Blueprint("auth", __name__)


def generate_demo_voter_id():
    last_user = (
        User.query.filter(User.voter_id.like("DEMO%"))
        .order_by(User.id.desc())
        .first()
    )
    if not last_user:
        return "DEMO001"

    try:
        next_number = int(last_user.voter_id.replace("DEMO", "")) + 1
    except ValueError:
        next_number = 1
    return f"DEMO{next_number:03d}"


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


@auth_bp.route("/")
def home():
    latest_election = Election.query.order_by(Election.id.desc()).first()
    public_results = None
    if latest_election and latest_election.status == "closed":
        rows = count_results_for_election(latest_election.id)
        total_voters = User.query.filter_by(role="voter").count()
        total_votes = Vote.query.filter_by(election_id=latest_election.id).count()
        public_results = {
            "election": latest_election,
            "rows": rows,
            "total_voters": total_voters,
            "total_votes": total_votes,
            "votes_remaining": max(total_voters - total_votes, 0),
            "percentage": round((total_votes / total_voters) * 100, 2) if total_voters else 0.0,
        }
    return render_template("index.html", latest_election=latest_election, public_results=public_results)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([name, email, password, confirm_password]):
            flash("Please fill in all registration fields.", "danger")
            return render_template("register.html")
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "danger")
            return render_template("register.html")
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("register.html")
        if "@" not in email or "." not in email:
            flash("Please enter a valid email address.", "danger")
            return render_template("register.html")

        generated_voter_id = generate_demo_voter_id()
        while User.query.filter_by(voter_id=generated_voter_id).first():
            generated_voter_id = generate_demo_voter_id()

        user = User(
            name=name,
            voter_id=generated_voter_id,
            email=email,
            password_hash=generate_password_hash(password),
            role="voter",
            has_voted=False,
        )
        db.session.add(user)
        db.session.commit()

        return render_template(
            "registration_success.html",
            name=user.name,
            email=user.email,
            voter_id=user.voter_id,
        )

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        voter_id = request.form.get("voter_id", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(voter_id=voter_id).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid Voter ID or password.", "danger")
            return render_template("login.html")

        session["user_id"] = user.id
        session["role"] = user.role
        flash("Login successful.", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.home"))


@auth_bp.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        flash("Please log in to access the voter dashboard.", "danger")
        return redirect(url_for("auth.login"))

    active_election = Election.query.filter_by(status="active").order_by(Election.id.desc()).first()
    return render_template("dashboard.html", user=user, active_election=active_election)


@auth_bp.route("/election/<int:election_id>")
def election_detail(election_id):
    user = get_current_user()
    if not user:
        flash("Please log in to view the election.", "danger")
        return redirect(url_for("auth.login"))

    election = Election.query.get_or_404(election_id)
    candidates = Candidate.query.filter_by(election_id=election.id).all()
    return render_template("election.html", election=election, candidates=candidates, user=user)


@auth_bp.route("/vote/<int:election_id>", methods=["POST"])
def cast_vote(election_id):
    user = get_current_user()
    if not user:
        flash("Please log in before casting a vote.", "danger")
        return redirect(url_for("auth.login"))

    election = Election.query.get_or_404(election_id)
    if election.status != "active":
        flash("This election is not active right now.", "danger")
        return redirect(url_for("auth.dashboard"))
    if user.has_voted:
        flash("You have already cast your vote.", "warning")
        return redirect(url_for("auth.dashboard"))

    candidate_id = request.form.get("candidate_id")
    if not candidate_id:
        flash("Please select a candidate.", "danger")
        return redirect(url_for("auth.election_detail", election_id=election.id))

    candidate = Candidate.query.filter_by(id=candidate_id, election_id=election.id).first()
    if not candidate:
        flash("Selected candidate is invalid.", "danger")
        return redirect(url_for("auth.election_detail", election_id=election.id))

    security = create_secure_vote(user.id, election.id, candidate.id)
    valid, decrypted = verify_secure_vote(
        user.id,
        election.id,
        candidate.id,
        security["encrypted_vote"],
        security["nonce"],
        security["authentication_tag"],
        security["signature"],
    )

    if not valid or not decrypted:
        flash("Vote signature verification failed. Vote rejected for security reasons.", "danger")
        return redirect(url_for("auth.election_detail", election_id=election.id))

    vote = Vote(
        election_id=election.id,
        voter_id=user.id,
        encrypted_vote=security["encrypted_vote"],
        nonce=security["nonce"],
        authentication_tag=security["authentication_tag"],
        signature=security["signature"],
    )
    db.session.add(vote)
    user.has_voted = True
    db.session.commit()

    flash("Your vote was securely recorded and acknowledged.", "success")
    return redirect(url_for("auth.receipt", vote_id=vote.id))


@auth_bp.route("/receipt/<int:vote_id>")
def receipt(vote_id):
    user = get_current_user()
    if not user:
        flash("Please log in to access your receipt.", "danger")
        return redirect(url_for("auth.login"))

    vote = Vote.query.filter_by(id=vote_id, voter_id=user.id).first_or_404()
    election = Election.query.get_or_404(vote.election_id)
    return render_template("receipt.html", vote=vote, election=election, user=user)
