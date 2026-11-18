from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash

from teamup.extensions import db
from teamup.forms import ActionForm, ProfileForm
from teamup.models.faculty import faculty_choices
from teamup.models.skill import Skill
from teamup.models.user import User

profile = Blueprint("profile", __name__)


@profile.route("/profile", methods=["GET", "POST"])
@login_required
def edit():
    # En GET muestra los datos actuales; en POST, lo que se envió
    form = ProfileForm(data={
        "username": current_user.username,
        "first_name": current_user.first_name,
        "middle_name": current_user.middle_name,
        "last_name": current_user.last_name,
        "second_last_name": current_user.second_last_name,
        "email": current_user.email,
        "faculty": current_user.major.faculty_id,
        "major": current_user.major_id,
        "semester": current_user.semester,
        "bio": current_user.bio,
        "skills": ", ".join(skill.name for skill in current_user.skills),
        "availability": current_user.availability,
        "phone": current_user.phone,
        "portfolio_url": current_user.portfolio_url,
        "linkedin_url": current_user.linkedin_url,
    })
    form.faculty.choices = faculty_choices()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.middle_name = form.middle_name.data or None
        current_user.last_name = form.last_name.data
        current_user.second_last_name = form.second_last_name.data or None
        current_user.email = form.email.data
        current_user.major_id = form.major.data
        current_user.semester = form.semester.data
        current_user.bio = form.bio.data or None
        current_user.skills = Skill.from_names(form.skill_names())
        current_user.availability = form.availability.data or None
        current_user.phone = form.phone.data or None
        current_user.portfolio_url = form.portfolio_url.data or None
        current_user.linkedin_url = form.linkedin_url.data or None

        if form.new_password.data:
            current_user.password_hash = generate_password_hash(form.new_password.data)

        db.session.commit()
        flash("Cambios guardados.", "success")
        return redirect(url_for("profile.edit"))

    return render_template("profile.html", form=form, delete_form=ActionForm())


@profile.route("/users/<username>")
@login_required
def public(username):
    """Perfil público: sobre mí, habilidades, disponibilidad, enlaces y proyectos."""
    person = User.query.filter_by(username=username.lower()).first_or_404()
    # Una cuenta desactivada solo la ve el admin
    if not person.is_active and not current_user.is_admin:
        abort(404)
    return render_template("profile_public.html", person=person)


@profile.route("/profile/delete", methods=["POST"])
@login_required
def delete():
    form = ActionForm()

    if form.validate_on_submit():
        user = db.session.get(User, current_user.id)
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash("Tu cuenta fue eliminada.", "success")
        return redirect(url_for("auth.login"))

    flash("No se pudo eliminar la cuenta. Inténtalo de nuevo.", "error")
    return redirect(url_for("profile.edit"))
