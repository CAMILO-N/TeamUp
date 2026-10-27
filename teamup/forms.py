from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import EmailField, PasswordField, SelectField, StringField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp, ValidationError,
)

from teamup.extensions import db
from teamup.models.major import Major
from teamup.models.user import User
from teamup.validators import EcuadorianIdNumber, InstitutionalEmail


# Filtros: limpian el dato antes de validarlo

def strip_spaces(value):
    return value.strip() if value else value


def lowercase(value):
    return value.lower() if value else value


def remove_separators(value):
    """Quita espacios y guiones: "171234567-8" queda como "1712345678"."""
    return value.replace(" ", "").replace("-", "") if value else value


def int_or_none(value):
    """La opción vacía "Elige" queda como None."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class RegisterForm(FlaskForm):
    username = StringField("Nombre de usuario", filters=[strip_spaces], validators=[
        DataRequired("Escribe un nombre de usuario."),
        Regexp(r"^[A-Za-z0-9_.]{3,25}$", message="De 3 a 25 caracteres: letras, números, punto o guion bajo."),
    ])
    first_name = StringField("Primer nombre", filters=[strip_spaces], validators=[
        DataRequired("Escribe tu primer nombre."),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    middle_name = StringField("Segundo nombre", filters=[strip_spaces], validators=[
        Optional(),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    last_name = StringField("Primer apellido", filters=[strip_spaces], validators=[
        DataRequired("Escribe tu primer apellido."),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    second_last_name = StringField("Segundo apellido", filters=[strip_spaces], validators=[
        Optional(),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    id_number = StringField("Cédula", filters=[remove_separators], validators=[
        DataRequired("Escribe tu cédula."),
        EcuadorianIdNumber(),
    ])
    email = EmailField("Correo institucional", filters=[strip_spaces, lowercase], validators=[
        DataRequired("Escribe tu correo."),
        Length(max=100, message="Máximo 100 caracteres."),
        Email("Ingresa un correo válido."),
        InstitutionalEmail(),
    ])
    # Las opciones se cargan desde la base en el controlador
    major = SelectField("Carrera", coerce=int_or_none, validate_choice=False, validators=[
        DataRequired("Elige tu carrera."),
    ])
    semester = SelectField("Semestre", coerce=int_or_none, validate_choice=False,
                           choices=[(n, str(n)) for n in range(1, 11)], validators=[
        DataRequired("Elige tu semestre."),
        NumberRange(1, 10, message="Elige un semestre del 1 al 10."),
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired("Escribe una contraseña."),
        Length(min=8, message="Mínimo 8 caracteres."),
    ])
    confirm_password = PasswordField("Confirmar contraseña", validators=[
        DataRequired("Repite tu contraseña."),
        EqualTo("password", message="Las contraseñas no coinciden."),
    ])

    # Reglas que consultan la base (WTForms ejecuta cada método validate_<campo>)

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Ese nombre de usuario ya está en uso.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Ya existe una cuenta con ese correo.")

    def validate_id_number(self, field):
        if User.query.filter_by(id_number=field.data).first():
            raise ValidationError("Ya existe una cuenta con esa cédula.")

    def validate_major(self, field):
        if db.session.get(Major, field.data) is None:
            raise ValidationError("Elige una carrera de la lista.")


class LoginForm(FlaskForm):
    identifier = StringField("Correo o nombre de usuario", filters=[strip_spaces], validators=[
        DataRequired("Escribe tu correo o nombre de usuario."),
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired("Escribe tu contraseña."),
    ])


class ProfileForm(RegisterForm):
    """Mismos datos del registro, con cambio de contraseña opcional."""

    # Poner un campo en None lo quita del formulario heredado.
    # La cédula no se puede cambiar desde el perfil.
    id_number = None
    password = None
    confirm_password = None

    current_password = PasswordField("Contraseña actual")
    new_password = PasswordField("Nueva contraseña", validators=[
        Optional(),
        Length(min=8, message="Mínimo 8 caracteres."),
    ])
    confirm_new_password = PasswordField("Confirmar nueva contraseña", validators=[
        EqualTo("new_password", message="Las contraseñas no coinciden."),
    ])

    # Mismas reglas de unicidad, sin contar al usuario actual

    def validate_username(self, field):
        taken = User.query.filter(User.username == field.data, User.id != current_user.id).first()
        if taken:
            raise ValidationError("Ese nombre de usuario ya está en uso.")

    def validate_email(self, field):
        taken = User.query.filter(User.email == field.data, User.id != current_user.id).first()
        if taken:
            raise ValidationError("Ya existe una cuenta con ese correo.")

    def validate_current_password(self, field):
        # Solo se pide si escribió una contraseña nueva
        if self.new_password.data:
            if not field.data or not check_password_hash(current_user.password_hash, field.data):
                raise ValidationError("La contraseña actual no es correcta.")


class DeleteAccountForm(FlaskForm):
    """Sin campos: solo lleva el token CSRF del botón de eliminar."""
