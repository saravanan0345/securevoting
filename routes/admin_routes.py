from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from models.models import Candidate, Election, User, Vote, db
from services.voting_service import count_results_for_election

admin_bp = Blueprint("admin", __name__)


def current_admin():
    admin_id = session.get("admin_id")
    if not admin_id:
        return None
    return db.session.get(User, admin_id)


@admin_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = User.query.filter_by(role="admin", voter_id=username).first()
        if not admin or not check_password_hash(admin.password_hash, password):
            flash("Invalid admin login details.", "danger")
            return render_template("admin_login.html")

        session["admin_id"] = admin.id
        session["role"] = "admin"
        flash("Admin login successful.", "success")
        return redirect(url_for("admin.admin_dashboard"))

    return render_template("admin_login.html")


@admin_bp.route("/admin/logout")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("role", None)
    flash("Admin logged out.", "success")
    return redirect(url_for("admin.admin_login"))


@admin_bp.route("/admin/dashboard")
def admin_dashboard():
    admin = current_admin()
    if not admin:
        flash("Please log in as admin.", "danger")
        return redirect(url_for("admin.admin_login"))

    elections = Election.query.order_by(Election.id.desc()).all()
    voters = User.query.filter_by(role="voter").order_by(User.id.asc()).all()
    candidates = Candidate.query.order_by(Candidate.id.asc()).all()
    total_voters = User.query.filter_by(role="voter").count()
    votes_cast = Vote.query.count()
    votes_remaining = max(total_voters - votes_cast, 0)
    active_election = Election.query.filter_by(status="active").order_by(Election.id.desc()).first()
    election_status = active_election.status if active_election else "No active election"

    return render_template(
        "admin_dashboard.html",
        admin=admin,
        elections=elections,
        voters=voters,
        candidates=candidates,
        total_voters=total_voters,
        votes_cast=votes_cast,
        votes_remaining=votes_remaining,
        election_status=election_status,
        active_election=active_election,
    )


@admin_bp.route("/admin/election/create", methods=["POST"])
def create_election():
    admin = current_admin()
    if not admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("admin.admin_login"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    if not all([name, description, start_date, end_date]):
        flash("Please provide election name, description, start date, and end date.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    election = Election(
        name=name,
        description=description,
        start_date=datetime.fromisoformat(start_date),
        end_date=datetime.fromisoformat(end_date),
        status="draft",
    )
    db.session.add(election)
    db.session.commit()

    flash("Election created successfully.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin/election/<int:election_id>/toggle", methods=["POST"])
def toggle_election(election_id):
    admin = current_admin()
    if not admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("admin.admin_login"))

    election = Election.query.get_or_404(election_id)
    if election.status == "active":
        election.status = "closed"
        flash("Election has been closed. Results are now available.", "success")
    else:
        election.status = "active"
        flash("Election reopened for voting.", "warning")
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin/candidate/add", methods=["POST"])
def add_candidate():
    admin = current_admin()
    if not admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("admin.admin_login"))

    name = request.form.get("name", "").strip()
    party = request.form.get("party", "").strip()
    symbol = request.form.get("symbol", "").strip() or "◉"
    election_id = request.form.get("election_id")

    if not all([name, party, election_id]):
        flash("Please provide candidate name, party, and election.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    candidate = Candidate(name=name, party=party, symbol=symbol, election_id=int(election_id))
    db.session.add(candidate)
    db.session.commit()
    flash("Candidate added successfully.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin/candidate/<int:candidate_id>/delete", methods=["POST"])
def delete_candidate(candidate_id):
    admin = current_admin()
    if not admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("admin.admin_login"))

    candidate = Candidate.query.get_or_404(candidate_id)
    db.session.delete(candidate)
    db.session.commit()
    flash("Candidate deleted successfully.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin/candidates")
def admin_candidates():
    admin = current_admin()
    if not admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("admin.admin_login"))

    candidates = Candidate.query.order_by(Candidate.id.asc()).all()
    return render_template("candidates.html", candidates=candidates, admin=admin)


@admin_bp.route("/admin/results")
def admin_results():
    admin = current_admin()
    if not admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("admin.admin_login"))

    elections = Election.query.order_by(Election.id.desc()).all()
    totals = []
    for election in elections:
        counts = count_results_for_election(election.id)
        total_voters = User.query.filter_by(role="voter").count()
        total_votes = Vote.query.filter_by(election_id=election.id).count()
        total_remaining = max(total_voters - total_votes, 0)
        percentage = round((total_votes / total_voters) * 100, 2) if total_voters else 0.0
        totals.append({
            "election": election,
            "rows": counts,
            "total_votes": total_votes,
            "total_remaining": total_remaining,
            "percentage": percentage,
            "total_voters": total_voters,
        })

    return render_template("results.html", totals=totals, admin=admin)
