from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import EmailField, PasswordField, SelectField, StringField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp, ValidationError,
)
from flask_login import current_user

from teamup.extensions import db
from teamup.models.carrera import Carrera
from teamup.models.usuario import Usuario


# --- Filtros: limpian el dato antes de validarlo ---

def quitar_espacios(valor):
    return valor.strip() if valor else valor


def minusculas(valor):
    return valor.lower() if valor else valor


def entero_o_none(valor):
    """Convierte la opción elegida a número; la opción vacía "Elige" queda como None."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


class RegistroForm(FlaskForm):
    usuario = StringField("Nombre de usuario", filters=[quitar_espacios], validators=[
        DataRequired("Escribe un nombre de usuario."),
        Regexp(r"^[A-Za-z0-9_.]{3,25}$", message="De 3 a 25 caracteres: letras, números, punto o guion bajo."),
    ])
    primer_nombre = StringField("Primer nombre", filters=[quitar_espacios], validators=[
        DataRequired("Escribe tu primer nombre."),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    segundo_nombre = StringField("Segundo nombre", filters=[quitar_espacios], validators=[
        Optional(),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    primer_apellido = StringField("Primer apellido", filters=[quitar_espacios], validators=[
        DataRequired("Escribe tu primer apellido."),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    segundo_apellido = StringField("Segundo apellido", filters=[quitar_espacios], validators=[
        Optional(),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    correo = EmailField("Correo institucional", filters=[quitar_espacios, minusculas], validators=[
        DataRequired("Escribe tu correo."),
        Length(max=100, message="Máximo 100 caracteres."),
        Email("Ingresa un correo válido."),
    ])
    # Las opciones de carrera se cargan desde la base en el controlador
    carrera = SelectField("Carrera", coerce=entero_o_none, validate_choice=False, validators=[
        DataRequired("Elige tu carrera."),
    ])
    semestre = SelectField("Semestre", coerce=entero_o_none, validate_choice=False,
                           choices=[(n, str(n)) for n in range(1, 11)], validators=[
        DataRequired("Elige tu semestre."),
        NumberRange(1, 10, message="Elige un semestre del 1 al 10."),
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired("Escribe una contraseña."),
        Length(min=8, message="Mínimo 8 caracteres."),
    ])
    password2 = PasswordField("Confirmar contraseña", validators=[
        DataRequired("Repite tu contraseña."),
        EqualTo("password", message="Las contraseñas no coinciden."),
    ])

    # WTForms ejecuta solo los métodos validate_<campo>, después de los validadores de arriba.
    # Aquí van las reglas que necesitan consultar la base de datos.

    def validate_usuario(self, campo):
        if Usuario.query.filter_by(nombreUsuario=campo.data).first():
            raise ValidationError("Ese nombre de usuario ya está en uso.")

    def validate_correo(self, campo):
        if Usuario.query.filter_by(emailUsuario=campo.data).first():
            raise ValidationError("Ya existe una cuenta con ese correo.")

    def validate_carrera(self, campo):
        if db.session.get(Carrera, campo.data) is None:
            raise ValidationError("Elige una carrera de la lista.")


class LoginForm(FlaskForm):
    correo = StringField("Correo o nombre de usuario", filters=[quitar_espacios], validators=[
        DataRequired("Escribe tu correo o nombre de usuario."),
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired("Escribe tu contraseña."),
    ])


class PerfilForm(RegistroForm):
    """Editar el perfil: los mismos datos del registro, pero sin contraseña."""

    # En WTForms, poner un campo en None lo quita del formulario heredado
    password = None
    password2 = None
    
    password_actual = PasswordField("Contraseña actual")
    password_nueva = PasswordField("Nueva contraseña", validators=[
        Optional(),
        Length(min=8, message="Mínimo 8 caracteres."),
    ])
    password_nueva2 = PasswordField("Confirmar nueva contraseña", validators=[
        EqualTo("password_nueva", message="Las contraseñas no coinciden."),
    ])

    # Mismas reglas del registro, pero ignorando a la propia persona:
    # si no cambia su alias o su correo, no debe salir "ya está en uso".

    def validate_usuario(self, campo):
        otro = Usuario.query.filter(
            Usuario.nombreUsuario == campo.data,
            Usuario.idUsuario != current_user.idUsuario,
        ).first()
        if otro:
            raise ValidationError("Ese nombre de usuario ya está en uso.")

    def validate_correo(self, campo):
        otro = Usuario.query.filter(
            Usuario.emailUsuario == campo.data,
            Usuario.idUsuario != current_user.idUsuario,
        ).first()
        if otro:
            raise ValidationError("Ya existe una cuenta con ese correo.")
    
    def validate_password_actual(self, campo):
        # Solo importa si escribió una contraseña nueva
        if self.password_nueva.data:
            if not campo.data or not check_password_hash(current_user.passwordUsuario, campo.data):
                raise ValidationError("La contraseña actual no es correcta.")
            
class EliminarCuentaForm(FlaskForm):
    """Sin campos: solo sirve para llevar el token CSRF del botón de eliminar cuenta."""