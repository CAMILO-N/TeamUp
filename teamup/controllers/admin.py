from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from teamup.controllers.projects import apply_project_action
from teamup.extensions import db
from teamup.forms import ActionForm
from teamup.models.project import Project
from teamup.models.role import ADMIN, Role
from teamup.models.user import User
from teamup.permissions import role_required

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/users")
@role_required(ADMIN)
def users():
    return render_template(
        "admin_users.html",
        users=User.query.order_by(User.username).all(),
        roles=Role.query.order_by(Role.id).all(),
        csrf_form=ActionForm(),
    )


@admin.route("/users/<int:user_id>/role", methods=["POST"])
@role_required(ADMIN)
def change_role(user_id):
    user = db.get_or_404(User, user_id)
    role = Role.query.filter_by(name=request.form.get("role")).first()

    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
    elif user.id == current_user.id:
        # Así nunca se queda el sistema sin administrador
        flash("No puedes cambiar tu propio rol.", "error")
    elif role is None:
        flash("Elige un rol de la lista.", "error")
    else:
        user.role = role
        db.session.commit()
        flash(f"@{user.username} ahora es {role.label.lower()}.", "success")

    return redirect(url_for("admin.users"))


@admin.route("/users/<int:user_id>/active", methods=["POST"])
@role_required(ADMIN)
def set_active(user_id):
    user = db.get_or_404(User, user_id)
    active = request.form.get("active")

    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
    elif user.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "error")
    elif active not in ("0", "1"):
        flash("Acción no válida.", "error")
    else:
        user.is_active = active == "1"
        db.session.commit()
        flash(f"La cuenta de @{user.username} fue {'activada' if user.is_active else 'desactivada'}.", "success")

    return redirect(url_for("admin.users"))


@admin.route("/projects")
@role_required(ADMIN)
def projects():
    return render_template(
        "admin_projects.html",
        projects=Project.query.order_by(Project.created_at.desc()).all(),
        csrf_form=ActionForm(),
    )


@admin.route("/projects/<int:project_id>/<any(hide, show, delete):action>", methods=["POST"])
@role_required(ADMIN)
def project_action(project_id, action):
    apply_project_action(db.get_or_404(Project, project_id), action)
    return redirect(url_for("admin.projects"))
