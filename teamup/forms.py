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


# Filters: clean the value before validating it

def strip_spaces(value):
    return value.strip() if value else value


def lowercase(value):
    return value.lower() if value else value


def int_or_none(value):
    """The empty "Elige" option becomes None."""
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
    email = EmailField("Correo institucional", filters=[strip_spaces, lowercase], validators=[
        DataRequired("Escribe tu correo."),
        Length(max=100, message="Máximo 100 caracteres."),
        Email("Ingresa un correo válido."),
    ])
    # Choices are loaded from the database in the controller
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

    # Rules that need the database (WTForms runs every validate_<field> method)

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Ese nombre de usuario ya está en uso.")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Ya existe una cuenta con ese correo.")

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
    """Same data as the register form, with an optional password change."""

    # Setting a field to None removes it from the inherited form
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

    # Same uniqueness rules, ignoring the current user

    def validate_username(self, field):
        taken = User.query.filter(User.username == field.data, User.id != current_user.id).first()
        if taken:
            raise ValidationError("Ese nombre de usuario ya está en uso.")

    def validate_email(self, field):
        taken = User.query.filter(User.email == field.data, User.id != current_user.id).first()
        if taken:
            raise ValidationError("Ya existe una cuenta con ese correo.")

    def validate_current_password(self, field):
        # Only required when a new password was typed
        if self.new_password.data:
            if not field.data or not check_password_hash(current_user.password_hash, field.data):
                raise ValidationError("La contraseña actual no es correcta.")


class DeleteAccountForm(FlaskForm):
    """No fields: it only carries the CSRF token for the delete button."""
