from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from teamup.extensions import db
from teamup.forms import LoginForm, RegisterForm
from teamup.models.faculty import faculty_choices
from teamup.models.role import STUDENT, Role
from teamup.models.user import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.explore"))

    form = RegisterForm()
    form.faculty.choices = faculty_choices()

    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            id_number=form.id_number.data,
            password_hash=generate_password_hash(form.password.data),
            semester=form.semester.data,
            major_id=form.major.data,
            role=Role.query.filter_by(name=STUDENT).one(),
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
        # Se puede entrar con el correo o con el nombre de usuario
        # El correo y el nombre de usuario se guardan en minúsculas
        identifier = form.identifier.data.lower()
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            if not user.is_active:
                flash("Tu cuenta está desactivada. Habla con un administrador.")
                return render_template("login.html", form=form)

            login_user(user)

            # Si venía de una página protegida, vuelve a ella
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
