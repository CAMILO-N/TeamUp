from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from teamup.extensions import db
from teamup.forms import ExploreFilterForm
from teamup.models.category import category_choices
from teamup.models.faculty import Faculty, faculty_choices
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
    # Los filtros vienen en la dirección: /explore?category=2&modality=remote
    form = ExploreFilterForm(request.args)
    form.category.choices = category_choices()
    form.faculty.choices = faculty_choices()
    filters = form.filters()

    return render_template(
        "explore.html",
        form=form,
        # Solo los publicados que buscan equipo; los borradores los ve su dueño en "Mis proyectos"
        projects=Project.search(**filters).all(),
        filtering=any(filters.values()),
    )


@main.route("/showcase")
@login_required
def showcase():
    # Vitrina: lo que ya se hizo en el campus
    return render_template("showcase.html", projects=Project.showcase().all())


@main.route("/faculties/<int:faculty_id>/majors")
def faculty_majors(faculty_id):
    """Carreras de una facultad en JSON. La usa la lista de carreras del registro y del perfil."""
    faculty = db.get_or_404(Faculty, faculty_id)
    return jsonify([{"id": major.id, "name": major.name} for major in faculty.majors])
