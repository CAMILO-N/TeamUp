from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from teamup.choices import APPLICATION_PENDING
from teamup.extensions import db
from teamup.forms import ActionForm, ApplicationForm
from teamup.models.application import Application
from teamup.models.notification import Notification
from teamup.models.project import Project
from teamup.models.vacancy import Vacancy

applications = Blueprint("applications", __name__)


# Postularse a un rol

@applications.route("/vacancies/<int:vacancy_id>/apply", methods=["GET", "POST"])
@login_required
def apply(vacancy_id):
    vacancy = db.get_or_404(Vacancy, vacancy_id)
    project = vacancy.project
    if not (project.is_public or project.owner_id == current_user.id):
        abort(404)

    # Las reglas se revisan en el servidor aunque la página no muestre el botón
    blocker = vacancy.apply_blocker(current_user)
    if blocker:
        flash(blocker, "error")
        return redirect(url_for("projects.detail", project_id=project.id))

    form = ApplicationForm()
    if form.validate_on_submit():
        # Si se había retirado, vuelve a postular con la misma fila (una por persona y rol)
        application = vacancy.application_of(current_user)
        if application is None:
            application = Application(vacancy=vacancy, user=current_user)
            db.session.add(application)
        application.message = form.message.data
        application.status = APPLICATION_PENDING
        application.decided_at = None
        Notification.send(project.owner,
                          f"@{current_user.username} se postuló al rol «{vacancy.role_name}» en «{project.title}».",
                          url_for("applications.manage", project_id=project.id))
        try:
            db.session.commit()
        except IntegrityError:
            # Dos envíos al mismo tiempo: la base no deja duplicar
            db.session.rollback()
            flash(f"Ya te postulaste al rol «{vacancy.role_name}».", "error")
            return redirect(url_for("projects.detail", project_id=project.id))
        flash(f"Te postulaste al rol «{vacancy.role_name}». El creador te responderá pronto.", "success")
        return redirect(url_for("applications.mine"))

    return render_template("application_new.html", form=form, vacancy=vacancy, project=project)


# Mis postulaciones

@applications.route("/my-applications")
@login_required
def mine():
    own = current_user.applications
    return render_template(
        "my_applications.html",
        pending=[a for a in own if a.is_pending],
        accepted=[a for a in own if a.is_accepted],
        closed=[a for a in own if not (a.is_pending or a.is_accepted)],
        csrf_form=ActionForm(),
    )


@applications.route("/applications/<int:application_id>/withdraw", methods=["POST"])
@login_required
def withdraw(application_id):
    application = db.get_or_404(Application, application_id)
    if application.user_id != current_user.id:
        abort(403)

    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
        return redirect(url_for("applications.mine"))

    was_accepted = application.is_accepted
    error = application.withdraw()
    if error:
        flash(error, "error")
    else:
        if was_accepted:
            # El creador tiene que saber que quedó un lugar libre
            Notification.send(application.project.owner,
                              f"@{current_user.username} salió del equipo de «{application.project.title}» "
                              f"(rol «{application.vacancy.role_name}»).",
                              url_for("projects.detail", project_id=application.project.id))
        db.session.commit()
        if was_accepted:
            flash(f"Saliste del equipo de «{application.project.title}».", "success")
        else:
            flash(f"Retiraste tu postulación a «{application.project.title}».", "success")
    return redirect(url_for("applications.mine"))


# Postulaciones de un proyecto (solo su creador)

@applications.route("/projects/<int:project_id>/applications")
@login_required
def manage(project_id):
    project = db.get_or_404(Project, project_id)
    if project.owner_id != current_user.id:
        abort(403)
    return render_template("project_applications.html", project=project, csrf_form=ActionForm())


@applications.route("/applications/<int:application_id>/<any(accept, reject):decision>", methods=["POST"])
@login_required
def decide(application_id, decision):
    application = db.get_or_404(Application, application_id)
    project = application.project
    # Solo el creador del proyecto acepta o rechaza
    if project.owner_id != current_user.id:
        abort(403)

    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
    elif project.is_finished:
        flash("Un proyecto terminado ya no cambia su equipo.", "error")
    else:
        error = application.accept() if decision == "accept" else application.reject()
        if error:
            db.session.rollback()
            flash(error, "error")
        else:
            role = application.vacancy.role_name
            if decision == "accept":
                Notification.send(application.user, f"¡Te aceptaron en «{project.title}» como «{role}»!",
                                  url_for("projects.detail", project_id=project.id))
            else:
                Notification.send(application.user, f"Tu postulación al rol «{role}» en «{project.title}» no fue aceptada.",
                                  url_for("applications.mine"))
            db.session.commit()
            name = f"@{application.user.username}"
            if decision == "accept":
                flash(f"{name} ahora es parte del equipo como «{application.vacancy.role_name}».", "success")
            else:
                flash(f"Rechazaste la postulación de {name}.", "success")
    return redirect(url_for("applications.manage", project_id=project.id))
