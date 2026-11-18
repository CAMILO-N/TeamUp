from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user

from teamup.choices import REVIEW_PENDING
from teamup.controllers.projects import apply_project_action
from teamup.extensions import db
from teamup.forms import ActionForm, BannedWordForm
from teamup.models.banned_word import BannedWord
from teamup.models.project import Project
from teamup.models.role import ADMIN, Role
from teamup.models.user import User
from teamup.models.validation_request import ValidationRequest
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


# Cola de revisión: proyectos que esperan al admin antes de verse en Explorar

@admin.route("/reviews")
@role_required(ADMIN)
def reviews():
    decided = (ValidationRequest.query.filter(ValidationRequest.status != REVIEW_PENDING)
               .order_by(ValidationRequest.reviewed_at.desc()).limit(20).all())
    return render_template("admin_reviews.html", pending=ValidationRequest.pending().all(), decided=decided,
                           csrf_form=ActionForm())


@admin.route("/reviews/<int:review_id>/<any(approve, reject):decision>", methods=["POST"])
@role_required(ADMIN)
def decide_review(review_id, decision):
    review = db.get_or_404(ValidationRequest, review_id)

    if not ActionForm().validate_on_submit():
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
    elif not review.is_pending:
        flash("Ese pedido ya fue revisado.", "error")
    elif decision == "approve":
        review.approve(current_user)
        db.session.commit()
        if review.is_showcase:
            flash(f"«{review.project.title}» ya aparece en la Vitrina.", "success")
        else:
            flash(f"«{review.project.title}» fue aprobado y vuelve a estar {review.project.status_label.lower()}.", "success")
    else:
        review.reject(current_user)
        db.session.commit()
        if review.is_showcase:
            flash(f"«{review.project.title}» no entra a la Vitrina.", "success")
        else:
            flash(f"«{review.project.title}» fue rechazado y volvió a borrador.", "success")

    return redirect(url_for("admin.reviews"))


# Filtro de palabras

@admin.route("/words", methods=["GET", "POST"])
@role_required(ADMIN)
def words():
    form = BannedWordForm()

    if form.validate_on_submit():
        db.session.add(BannedWord(word=form.word.data))
        db.session.commit()
        flash(f"«{form.word.data}» se agregó al filtro.", "success")
        return redirect(url_for("admin.words"))

    return render_template("admin_words.html", form=form, words=BannedWord.query.order_by(BannedWord.word).all(),
                           csrf_form=ActionForm())


@admin.route("/words/<int:word_id>/delete", methods=["POST"])
@role_required(ADMIN)
def delete_word(word_id):
    banned = db.get_or_404(BannedWord, word_id)

    if ActionForm().validate_on_submit():
        db.session.delete(banned)
        db.session.commit()
        flash(f"«{banned.word}» ya no está en el filtro.", "success")
    else:
        flash("El formulario expiró. Vuelve a intentarlo.", "error")
    return redirect(url_for("admin.words"))
