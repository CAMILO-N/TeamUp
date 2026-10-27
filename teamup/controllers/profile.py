from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash

from teamup.extensions import db
from teamup.forms import DeleteAccountForm, ProfileForm
from teamup.models.major import major_choices
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
        "major": current_user.major_id,
        "semester": current_user.semester,
    })
    form.major.choices = major_choices()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.middle_name = form.middle_name.data or None
        current_user.last_name = form.last_name.data
        current_user.second_last_name = form.second_last_name.data or None
        current_user.email = form.email.data
        current_user.major_id = form.major.data
        current_user.semester = form.semester.data

        if form.new_password.data:
            current_user.password_hash = generate_password_hash(form.new_password.data)

        db.session.commit()
        flash("Cambios guardados.", "success")
        return redirect(url_for("profile.edit"))

    return render_template("profile.html", form=form, delete_form=DeleteAccountForm())


@profile.route("/profile/delete", methods=["POST"])
@login_required
def delete():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        user = db.session.get(User, current_user.id)
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash("Tu cuenta fue eliminada.", "success")
        return redirect(url_for("auth.login"))

    flash("No se pudo eliminar la cuenta. Inténtalo de nuevo.", "error")
    return redirect(url_for("profile.edit"))
