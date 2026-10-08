from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from teamup.extensions import db
from teamup.forms import LoginForm, RegistroForm
from teamup.models.carrera import Carrera
from teamup.models.usuario import Usuario

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("principal.explorar"))

    form = RegistroForm()
    form.carrera.choices = [
        (c.idCarrera, c.nombreCarrera)
        for c in Carrera.query.order_by(Carrera.nombreCarrera).all()
    ]

    # Es POST y todos los validadores de RegistroForm pasaron
    if form.validate_on_submit():
        nuevo = Usuario(
            nombreUsuario=form.usuario.data,
            primerNombreUsuario=form.primer_nombre.data,
            segundoNombreUsuario=form.segundo_nombre.data or None,
            primerApellidoUsuario=form.primer_apellido.data,
            segundoApellidoUsuario=form.segundo_apellido.data or None,
            emailUsuario=form.correo.data,
            passwordUsuario=generate_password_hash(form.password.data),
            semestreUsuario=form.semestre.data,
            carreraUsuario=form.carrera.data,
        )
        db.session.add(nuevo)
        db.session.commit()

        login_user(nuevo)
        return redirect(url_for("principal.explorar"))

    # GET, o POST con errores: se muestra el formulario (con los errores en cada campo)
    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("principal.explorar"))

    form = LoginForm()

    if form.validate_on_submit():
        # Se puede entrar con el correo o con el nombre de usuario
        identificador = form.correo.data
        usuario = Usuario.query.filter(
            (Usuario.emailUsuario == identificador.lower()) | (Usuario.nombreUsuario == identificador)
        ).first()

        if usuario and check_password_hash(usuario.passwordUsuario, form.password.data):
            login_user(usuario)

            # Si venía de una página protegida, volver a ella
            siguiente = request.args.get("next")
            if siguiente and siguiente.startswith("/") and not siguiente.startswith("//"):
                return redirect(siguiente)
            return redirect(url_for("principal.explorar"))

        # No se dice cuál de los dos falló, a propósito
        flash("Correo o contraseña incorrectos.")

    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
