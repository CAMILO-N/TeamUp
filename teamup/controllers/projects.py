from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from teamup.extensions import db
from teamup.forms import ActionForm, ProjectForm
from teamup.models.project import Project

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


@projects.route("/projects/new", methods=["GET", "POST"])
@login_required
def new():
    form = ProjectForm()

    if form.validate_on_submit():
        project = Project(title=form.title.data, description=form.description.data, owner=current_user)
        db.session.add(project)
        db.session.commit()
        flash("Tu proyecto ya está publicado.", "success")
        return redirect(url_for("main.explore"))

    return render_template("project_new.html", form=form)


@projects.route("/projects/<int:project_id>/<any(hide, show, delete):action>", methods=["POST"])
@login_required
def project_action(project_id, action):
    project = db.get_or_404(Project, project_id)
    # El dueño solo maneja sus proyectos; el administrador usa su propio panel
    if project.owner_id != current_user.id:
        abort(403)

    apply_project_action(project, action)
    return redirect(url_for("main.explore"))
