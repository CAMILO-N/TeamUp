from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from teamup.choices import PROJECT_CANCELLED, PROJECT_DRAFT, PROJECT_FINISHED, PROJECT_OPEN
from teamup.extensions import db
from teamup.forms import ActionForm, ProjectDatesForm, ProjectInfoForm, VacancyForm
from teamup.models.category import category_choices
from teamup.models.faculty import faculty_choices
from teamup.models.project import Project
from teamup.models.vacancy import Vacancy

projects = Blueprint("projects", __name__)


def apply_project_action(project, action):
    """Oculta, muestra o borra un proyecto. La usan el dueño y el administrador."""
    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
        return

    if action == "hide":
        project.is_hidden = True
        message = f"«{project.title}» ya no aparece en Explorar."
    elif action == "show":
        project.is_hidden = False
        message = f"«{project.title}» vuelve a aparecer en Explorar."
    else:
        db.session.delete(project)
        message = f"«{project.title}» fue eliminado."

    db.session.commit()
    flash(message, "success")


def own_project(project_id):
    """El proyecto, si existe y es del usuario actual. Si no, 404 o 403."""
    project = db.get_or_404(Project, project_id)
    if project.owner_id != current_user.id:
        abort(403)
    return project


IN_REVIEW_MESSAGE = "Tu proyecto quedó en revisión: un administrador lo revisará antes de que aparezca en Explorar."


def review_after_edit(project):
    """Un proyecto ya publicado que se edita vuelve a pasar por el filtro de palabras."""
    if not project.is_draft and project.check_banned_words():
        db.session.commit()
        flash(IN_REVIEW_MESSAGE, "info")


def next_step(project, step):
    """En un borrador se sigue al paso siguiente; en uno publicado se vuelve a la vista previa."""
    return url_for(step if project.is_draft else "projects.preview", project_id=project.id)


# Paso 1: información

@projects.route("/projects/new", methods=["GET", "POST"])
@login_required
def new():
    form = ProjectInfoForm()
    form.category.choices = category_choices()

    if form.validate_on_submit():
        # Se guarda desde el paso 1 como borrador para no perder lo avanzado
        project = Project(owner=current_user, title=form.title.data, summary=form.summary.data,
                          description=form.description.data, category_id=form.category.data)
        db.session.add(project)
        db.session.commit()
        return redirect(url_for("projects.roles", project_id=project.id))

    return render_template("project_step_info.html", form=form, project=None)


@projects.route("/projects/<int:project_id>/info", methods=["GET", "POST"])
@login_required
def info(project_id):
    project = own_project(project_id)
    form = ProjectInfoForm(data={"title": project.title, "summary": project.summary,
                                 "description": project.description, "category": project.category_id})
    form.category.choices = category_choices()

    if form.validate_on_submit():
        project.title = form.title.data
        project.summary = form.summary.data
        project.description = form.description.data
        project.category_id = form.category.data
        db.session.commit()
        review_after_edit(project)
        return redirect(next_step(project, "projects.roles"))

    return render_template("project_step_info.html", form=form, project=project)


# Paso 2: roles (vacantes)

@projects.route("/projects/<int:project_id>/roles", methods=["GET", "POST"])
@login_required
def roles(project_id):
    project = own_project(project_id)
    form = VacancyForm()
    form.faculty.choices = faculty_choices()

    if form.validate_on_submit():
        project.vacancies.append(Vacancy(
            role_name=form.role_name.data,
            major_id=form.major.data if form.faculty.data is not None else None,
            requires_experience=form.requires_experience.data,
            slots=form.slots.data,
        ))
        db.session.commit()
        flash(f"Se agregó el rol «{form.role_name.data}».", "success")
        review_after_edit(project)
        return redirect(url_for("projects.roles", project_id=project.id))

    return render_template("project_step_roles.html", form=form, project=project, csrf_form=ActionForm())


@projects.route("/projects/<int:project_id>/roles/<int:vacancy_id>/delete", methods=["POST"])
@login_required
def delete_role(project_id, vacancy_id):
    project = own_project(project_id)
    vacancy = db.get_or_404(Vacancy, vacancy_id)
    if vacancy.project_id != project.id:
        abort(404)

    if ActionForm().validate_on_submit():
        db.session.delete(vacancy)
        db.session.commit()
        flash(f"Se quitó el rol «{vacancy.role_name}».", "success")
    else:
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
    return redirect(url_for("projects.roles", project_id=project.id))


# Paso 3: fechas, dedicación y modalidad

@projects.route("/projects/<int:project_id>/dates", methods=["GET", "POST"])
@login_required
def dates(project_id):
    project = own_project(project_id)
    form = ProjectDatesForm(data={"start_date": project.start_date, "estimated_end_date": project.estimated_end_date,
                                  "weekly_hours": project.weekly_hours, "modality": project.modality})

    if form.validate_on_submit():
        project.start_date = form.start_date.data
        project.estimated_end_date = form.estimated_end_date.data
        project.weekly_hours = form.weekly_hours.data
        project.modality = form.modality.data
        db.session.commit()
        return redirect(url_for("projects.preview", project_id=project.id))

    return render_template("project_step_dates.html", form=form, project=project)


# Paso 4: vista previa y publicar

@projects.route("/projects/<int:project_id>/preview")
@login_required
def preview(project_id):
    project = own_project(project_id)
    return render_template("project_preview.html", project=project, missing=project.missing_for_publish(),
                           csrf_form=ActionForm())


@projects.route("/projects/<int:project_id>/publish", methods=["POST"])
@login_required
def publish(project_id):
    project = own_project(project_id)

    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
        return redirect(url_for("projects.preview", project_id=project.id))

    missing = project.missing_for_publish()
    if missing:
        flash("Antes de publicar falta: " + ", ".join(missing) + ".", "error")
        return redirect(url_for("projects.preview", project_id=project.id))

    if project.is_draft:
        # Con una palabra del filtro queda en revisión; si no, se publica
        if project.check_banned_words():
            flash(IN_REVIEW_MESSAGE, "info")
        else:
            project.status = PROJECT_OPEN
            flash("Tu proyecto ya está publicado.", "success")
        db.session.commit()
    return redirect(url_for("projects.detail", project_id=project.id))


# Detalle

@projects.route("/projects/<int:project_id>")
@login_required
def detail(project_id):
    project = db.get_or_404(Project, project_id)
    is_owner = project.owner_id == current_user.id
    # Un borrador o un proyecto oculto solo lo ven su dueño y el admin
    if not (project.is_public or is_owner or current_user.is_admin):
        abort(404)
    # El dueño ve además el panel de gestión (estado, editar, ocultar, borrar)
    return render_template("project_detail.html", project=project, is_owner=is_owner,
                           csrf_form=ActionForm() if is_owner else None)


# Mis proyectos

@projects.route("/my-projects")
@login_required
def mine():
    own = current_user.projects
    return render_template(
        "my_projects.html",
        drafts=[p for p in own if p.status == PROJECT_DRAFT],
        active=[p for p in own if p.status not in (PROJECT_DRAFT, PROJECT_FINISHED, PROJECT_CANCELLED)],
        finished=[p for p in own if p.status == PROJECT_FINISHED],
    )


# Gestión del estado: arrancar, volver a buscar gente y terminar

@projects.route("/projects/<int:project_id>/<any(start, reopen, finish):change>", methods=["POST"])
@login_required
def change_status(project_id, change):
    project = own_project(project_id)

    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
        return redirect(url_for("projects.detail", project_id=project.id))

    error = {"start": project.start, "reopen": project.reopen,
             "finish": lambda: project.finish(date.today())}[change]()
    if error:
        flash(error, "error")
    else:
        db.session.commit()
        if change == "start":
            flash(f"«{project.title}» arrancó. Ya no aparece en Explorar.", "success")
        elif change == "reopen":
            flash(f"«{project.title}» vuelve a buscar gente en Explorar.", "success")
        elif project.duration_days is not None:
            flash(f"«{project.title}» quedó como terminado. Duró {project.duration_days} días.", "success")
        else:
            flash(f"«{project.title}» quedó como terminado.", "success")
    return redirect(url_for("projects.detail", project_id=project.id))


@projects.route("/projects/<int:project_id>/<any(hide, show, delete):action>", methods=["POST"])
@login_required
def project_action(project_id, action):
    # El dueño solo maneja sus proyectos; el administrador usa su propio panel
    project = own_project(project_id)
    apply_project_action(project, action)
    # Ocultar o mostrar vuelve a la gestión del proyecto; si se borró, a Mis proyectos
    if action == "delete":
        return redirect(url_for("projects.mine"))
    return redirect(url_for("projects.detail", project_id=project.id))
