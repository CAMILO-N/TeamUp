from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from teamup.extensions import db
from teamup.forms import ReportForm
from teamup.models.notification import Notification
from teamup.models.project import Project
from teamup.models.report import Report

reports = Blueprint("reports", __name__)


@reports.route("/projects/<int:project_id>/report", methods=["GET", "POST"])
@login_required
def new(project_id):
    project = db.get_or_404(Project, project_id)
    if not project.is_public:
        abort(404)

    if project.owner_id == current_user.id:
        flash("No puedes reportar tu propio proyecto.", "error")
        return redirect(url_for("projects.detail", project_id=project.id))
    if not project.can_be_reported:
        flash("Este proyecto ya no se puede reportar.", "error")
        return redirect(url_for("projects.detail", project_id=project.id))
    if Report.query.filter_by(project_id=project.id, user_id=current_user.id).first():
        flash("Ya reportaste este proyecto. Un administrador lo está revisando.", "info")
        return redirect(url_for("projects.detail", project_id=project.id))

    form = ReportForm()
    if form.validate_on_submit():
        # Con el reporte el proyecto sale de Explorar y entra a la cola del admin
        project.report(current_user, form.reason.data, form.detail.data)
        # El creador sabe que está en revisión, pero no quién lo reportó
        Notification.send(project.owner, f"«{project.title}» recibió un reporte y quedó en revisión. "
                                         "Un administrador lo revisará pronto.",
                          url_for("projects.detail", project_id=project.id))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Ya reportaste este proyecto.", "info")
            return redirect(url_for("main.explore"))
        flash("Gracias por avisar. Un administrador revisará el proyecto.", "success")
        return redirect(url_for("main.explore"))

    return render_template("report_new.html", form=form, project=project)
