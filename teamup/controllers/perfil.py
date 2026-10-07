from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash

from teamup.extensions import db
from teamup.forms import EliminarCuentaForm, PerfilForm
from teamup.models.carrera import Carrera
from teamup.models.usuario import Usuario

perfil = Blueprint("perfil", __name__)


@perfil.route("/perfil", methods=["GET", "POST"])
@login_required
def editar():
    # En un GET el formulario se llena con los datos actuales; en un POST, con lo que se envió
    form = PerfilForm(data={
        "usuario": current_user.nombreUsuario,
        "primer_nombre": current_user.primerNombreUsuario,
        "segundo_nombre": current_user.segundoNombreUsuario,
        "primer_apellido": current_user.primerApellidoUsuario,
        "segundo_apellido": current_user.segundoApellidoUsuario,
        "correo": current_user.emailUsuario,
        "carrera": current_user.carreraUsuario,
        "semestre": current_user.semestreUsuario,
    })
    form.carrera.choices = [
        (c.idCarrera, c.nombreCarrera)
        for c in Carrera.query.order_by(Carrera.nombreCarrera).all()
    ]

    if form.validate_on_submit():
        current_user.nombreUsuario = form.usuario.data
        current_user.primerNombreUsuario = form.primer_nombre.data
        current_user.segundoNombreUsuario = form.segundo_nombre.data or None
        current_user.primerApellidoUsuario = form.primer_apellido.data
        current_user.segundoApellidoUsuario = form.segundo_apellido.data or None
        current_user.emailUsuario = form.correo.data
        current_user.carreraUsuario = form.carrera.data
        current_user.semestreUsuario = form.semestre.data

        # La contraseña solo cambia si escribió una nueva (la actual ya se validó en el formulario)
        if form.password_nueva.data:
            current_user.passwordUsuario = generate_password_hash(form.password_nueva.data)

        db.session.commit()
        flash("Cambios guardados.", "ok")
        return redirect(url_for("perfil.editar"))

    return render_template("perfil.html", form=form, eliminar_form=EliminarCuentaForm())


@perfil.route("/perfil/eliminar", methods=["POST"])
@login_required
def eliminar():
    form = EliminarCuentaForm()
    
    if form.is_submitted() and not form.validate():
        print("ERRORES DEL FORMULARIO:", form.errors)  

    if form.validate_on_submit():
        usuario = db.session.get(Usuario, current_user.idUsuario)
        logout_user()
        db.session.delete(usuario)
        db.session.commit()
        flash("Tu cuenta fue eliminada.", "ok")
        return redirect(url_for("auth.login"))

    flash("No se pudo eliminar la cuenta. Inténtalo de nuevo.", "error")
    return redirect(url_for("perfil.editar"))