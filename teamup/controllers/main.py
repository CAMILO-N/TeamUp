from flask import Blueprint, jsonify, redirect, render_template, url_for
from flask_login import current_user, login_required

from teamup.extensions import db
from teamup.forms import ActionForm
from teamup.models.faculty import Faculty
from teamup.models.project import Project

main = Blueprint("main", __name__)


@main.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.explore"))
    return render_template("index.html")


@main.route("/explore")
@login_required
def explore():
    return render_template(
        "explore.html",
        projects=Project.query.filter_by(is_hidden=False).order_by(Project.created_at.desc()).all(),
        my_projects=current_user.projects,
        csrf_form=ActionForm(),
    )


@main.route("/faculties/<int:faculty_id>/majors")
def faculty_majors(faculty_id):
    """Carreras de una facultad en JSON. La usa la lista de carreras del registro y del perfil."""
    faculty = db.get_or_404(Faculty, faculty_id)
    return jsonify([{"id": major.id, "name": major.name} for major in faculty.majors])
