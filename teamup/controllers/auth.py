from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from teamup.extensions import db
from teamup.forms import LoginForm, RegisterForm
from teamup.models.major import major_choices
from teamup.models.user import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.explore"))

    form = RegisterForm()
    form.major.choices = major_choices()

    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data or None,
            last_name=form.last_name.data,
            second_last_name=form.second_last_name.data or None,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            semester=form.semester.data,
            major_id=form.major.data,
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("main.explore"))

    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.explore"))

    form = LoginForm()

    if form.validate_on_submit():
        # Users can sign in with their email or their username
        identifier = form.identifier.data
        user = User.query.filter(
            (User.email == identifier.lower()) | (User.username == identifier)
        ).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)

            # Go back to the protected page they came from
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect(url_for("main.explore"))

        flash("Correo o contraseña incorrectos.")

    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
