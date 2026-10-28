from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import EmailField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp, ValidationError,
)

from teamup.extensions import db
from teamup.models.faculty import Faculty
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


class UserDataForm(FlaskForm):
    """Datos que comparten el registro y el perfil. Los hijos solo agregan campos, nunca quitan."""

    # En el perfil no cuenta el propio usuario al revisar si el alias o el correo ya están en uso
    ignore_current_user = False

    username = StringField("Nombre de usuario", filters=[strip_spaces], validators=[
        DataRequired("Escribe un nombre de usuario."),
        Regexp(r"^[A-Za-z0-9_.]{3,25}$", message="De 3 a 25 caracteres: letras, números, punto o guion bajo."),
    ])
    first_name = StringField("Primer nombre", filters=[strip_spaces], validators=[
        DataRequired("Escribe tu primer nombre."),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    last_name = StringField("Primer apellido", filters=[strip_spaces], validators=[
        DataRequired("Escribe tu primer apellido."),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    email = EmailField("Correo institucional", filters=[strip_spaces, lowercase], validators=[
        DataRequired("Escribe tu correo."),
        Length(max=100, message="Máximo 100 caracteres."),
        Email("Ingresa un correo válido."),
        InstitutionalEmail(),
    ])
    # Las facultades se cargan en el controlador; las carreras las pide el navegador según la facultad
    faculty = SelectField("Facultad", coerce=int_or_none, validate_choice=False, validators=[
        DataRequired("Elige tu facultad."),
    ])
    major = SelectField("Carrera", coerce=int_or_none, validate_choice=False, validators=[
        DataRequired("Elige tu carrera."),
    ])
    semester = SelectField("Semestre", coerce=int_or_none, validate_choice=False,
                           choices=[(n, str(n)) for n in range(1, 11)], validators=[
        DataRequired("Elige tu semestre."),
        NumberRange(1, 10, message="Elige un semestre del 1 al 10."),
    ])

    # Reglas que consultan la base (WTForms ejecuta cada método validate_<campo>)

    def _is_taken(self, column, value):
        query = User.query.filter(column == value)
        if self.ignore_current_user:
            query = query.filter(User.id != current_user.id)
        return query.first() is not None

    def validate_username(self, field):
        if self._is_taken(User.username, field.data):
            raise ValidationError("Ese nombre de usuario ya está en uso.")

    def validate_email(self, field):
        if self._is_taken(User.email, field.data):
            raise ValidationError("Ya existe una cuenta con ese correo.")

    def validate_faculty(self, field):
        if db.session.get(Faculty, field.data) is None:
            raise ValidationError("Elige una facultad de la lista.")

    def validate_major(self, field):
        # La carrera tiene que ser de la facultad elegida, aunque alguien cambie la página
        major = db.session.get(Major, field.data)
        if major is None or major.faculty_id != self.faculty.data:
            raise ValidationError("Elige una carrera de tu facultad.")


class RegisterForm(UserDataForm):
    """Registro: solo lo necesario. El segundo nombre y apellido se completan en el perfil."""

    id_number = StringField("Cédula", filters=[remove_separators], validators=[
        DataRequired("Escribe tu cédula."),
        EcuadorianIdNumber(),
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired("Escribe una contraseña."),
        Length(min=8, message="Mínimo 8 caracteres."),
    ])
    confirm_password = PasswordField("Confirmar contraseña", validators=[
        DataRequired("Repite tu contraseña."),
        EqualTo("password", message="Las contraseñas no coinciden."),
    ])

    def validate_id_number(self, field):
        if self._is_taken(User.id_number, field.data):
            raise ValidationError("Ya existe una cuenta con esa cédula.")


class LoginForm(FlaskForm):
    identifier = StringField("Correo o nombre de usuario", filters=[strip_spaces], validators=[
        DataRequired("Escribe tu correo o nombre de usuario."),
    ])
    password = PasswordField("Contraseña", validators=[
        DataRequired("Escribe tu contraseña."),
    ])


class ProfileForm(UserDataForm):
    """Perfil: los datos del registro más los opcionales y el cambio de contraseña. La cédula no se edita."""

    ignore_current_user = True

    middle_name = StringField("Segundo nombre", filters=[strip_spaces], validators=[
        Optional(),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    second_last_name = StringField("Segundo apellido", filters=[strip_spaces], validators=[
        Optional(),
        Length(max=25, message="Máximo 25 caracteres."),
    ])
    current_password = PasswordField("Contraseña actual")
    new_password = PasswordField("Nueva contraseña", validators=[
        Optional(),
        Length(min=8, message="Mínimo 8 caracteres."),
    ])
    confirm_new_password = PasswordField("Confirmar nueva contraseña", validators=[
        EqualTo("new_password", message="Las contraseñas no coinciden."),
    ])

    def validate_current_password(self, field):
        # Solo se pide si escribió una contraseña nueva
        if self.new_password.data:
            if not field.data or not check_password_hash(current_user.password_hash, field.data):
                raise ValidationError("La contraseña actual no es correcta.")


class ProjectForm(FlaskForm):
    title = StringField("Título", filters=[strip_spaces], validators=[
        DataRequired("Escribe un título."),
        Length(max=80, message="Máximo 80 caracteres."),
    ])
    description = TextAreaField("Descripción", filters=[strip_spaces], validators=[
        DataRequired("Cuenta de qué se trata tu proyecto."),
        Length(max=1000, message="Máximo 1000 caracteres."),
    ])


class ActionForm(FlaskForm):
    """Sin campos: solo lleva el token CSRF de los botones (eliminar, ocultar, cambiar rol...)."""
