from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from sqlalchemy.orm import joinedload, selectinload

from teamup.extensions import db
from teamup.forms import ExploreFilterForm
from teamup.models.category import Category
from teamup.models.faculty import Faculty, faculty_choices
from teamup.models.project import Project
from teamup.models.vacancy import Vacancy

main = Blueprint("main", __name__)

# Lo que necesita la tarjeta de un proyecto, cargado en pocas consultas en lugar de una por tarjeta
CARD_DATA = (
    joinedload(Project.owner),
    joinedload(Project.category),
    selectinload(Project.vacancies).selectinload(Vacancy.applications),
    # La carrera de cada rol (y su facultad) la usa el filtro instantáneo de Explorar
    selectinload(Project.vacancies).joinedload(Vacancy.major),
)


def filter_data(project):
    """Datos de una tarjeta para static/js/explore-filters.js. Siguen las mismas reglas que Project.search():
    por carrera o facultad cuentan los roles abiertos para esa carrera o para cualquier carrera."""
    roles = [v for v in project.vacancies if v.is_open]
    with_major = [v for v in roles if v.major is not None]
    return {
        "project": project.id,
        "category": project.category_id or "",
        "modality": project.modality or "",
        "hours": project.weekly_hours or "",
        "majors": " ".join(sorted({str(v.major_id) for v in with_major})),
        "faculties": " ".join(sorted({str(v.major.faculty_id) for v in with_major})),
        "any-major": "1" if len(with_major) < len(roles) else "0",
    }


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
    categories = Category.query.order_by(Category.name).all()
    form.category.choices = [(category.id, category.name) for category in categories]
    form.faculty.choices = faculty_choices()
    filters = form.filters()
    filtering = any(filters.values())

    # Todos los que buscan equipo, con lo que muestran las tarjetas cargado de una vez
    # (sin esto, cada tarjeta pedía a la base sus roles, postulaciones, creador y categoría por separado)
    open_projects = Project.search().options(*CARD_DATA).all()

    # La página lleva todos los abiertos: static/js/explore-filters.js los filtra al instante en el navegador.
    # Con filtros en la dirección, la base dice cuáles coinciden y el resto empieza escondido
    # (así la página también funciona sin JavaScript)
    if filtering:
        matching = {row.id for row in Project.search(**filters).with_entities(Project.id)}
    else:
        matching = {p.id for p in open_projects}

    # Lo que el filtro instantáneo necesita de cada tarjeta (van como data-* en el HTML)
    card_data = {p.id: filter_data(p) for p in open_projects}

    # Los atajos de categoría conservan los demás filtros
    other_filters = {key: value for key, value in request.args.items()
                     if key in ("faculty", "major", "modality", "weekly_hours") and value}

    # Para tu carrera: tienen un rol abierto con lugar para tu carrera (o para cualquiera) y no son tuyos
    my_major = current_user.major_id
    for_you = [p for p in open_projects if p.owner_id != current_user.id and any(
        v.is_open and v.free_slots and v.major_id in (None, my_major) for v in p.vacancies)]

    return render_template(
        "explore.html",
        form=form,
        # Solo los publicados que buscan equipo; los borradores los ve su dueño en "Mis proyectos"
        projects=open_projects,
        matching=matching,
        card_data=card_data,
        other_filters=other_filters,
        filtering=filtering,
        categories=categories,
        stats={
            "projects": len(open_projects),
            "slots": sum(p.free_slots for p in open_projects),
            "for_you": len(for_you),
        },
        # Sin filtros se muestran arriba, como mucho tres, los que buscan a alguien como tú
        for_you=[] if filtering else for_you[:3],
    )


@main.route("/showcase")
@login_required
def showcase():
    # Vitrina: lo que ya se hizo en el campus
    return render_template("showcase.html", projects=Project.showcase().options(*CARD_DATA).all())


@main.route("/faculties/<int:faculty_id>/majors")
def faculty_majors(faculty_id):
    """Carreras de una facultad en JSON. La usa la lista de carreras del registro y del perfil."""
    faculty = db.get_or_404(Faculty, faculty_id)
    return jsonify([{"id": major.id, "name": major.name} for major in faculty.majors])
