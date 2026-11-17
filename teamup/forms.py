from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms import (
    BooleanField, DateField, EmailField, IntegerField, PasswordField, SelectField, StringField, TextAreaField,
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, InputRequired, Length, NumberRange, Optional, Regexp, ValidationError,
)

from teamup.choices import MODALITIES, WEEKLY_HOURS
from teamup.extensions import db
from teamup.models.category import Category
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

    # En minúsculas para que "Camilo_N" y "camilo_n" sean el mismo usuario en cualquier base
    username = StringField("Nombre de usuario", filters=[strip_spaces, lowercase], validators=[
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


class ProjectInfoForm(FlaskForm):
    """Paso 1 de crear un proyecto: de qué se trata."""

    title = StringField("Título", filters=[strip_spaces], validators=[
        DataRequired("Escribe un título."),
        Length(max=80, message="Máximo 80 caracteres."),
    ])
    summary = StringField("Resumen", filters=[strip_spaces], validators=[
        DataRequired("Escribe un resumen corto."),
        Length(max=200, message="Máximo 200 caracteres."),
    ])
    description = TextAreaField("Descripción", filters=[strip_spaces], validators=[
        DataRequired("Cuenta de qué se trata tu proyecto."),
        Length(max=3000, message="Máximo 3000 caracteres."),
    ])
    # Las opciones se cargan en el controlador
    category = SelectField("Categoría", coerce=int_or_none, validate_choice=False, validators=[
        DataRequired("Elige una categoría."),
    ])

    def validate_category(self, field):
        if db.session.get(Category, field.data) is None:
            raise ValidationError("Elige una categoría de la lista.")


class VacancyForm(FlaskForm):
    """Paso 2: un rol que busca el proyecto. Sin facultad = cualquier carrera."""

    role_name = StringField("Rol", filters=[strip_spaces], validators=[
        DataRequired("Escribe el nombre del rol."),
        Length(max=60, message="Máximo 60 caracteres."),
    ])
    faculty = SelectField("Facultad", coerce=int_or_none, validate_choice=False, validators=[Optional()])
    # Sin Optional(): si eligió facultad, validate_major tiene que correr aunque la carrera llegue vacía
    major = SelectField("Carrera", coerce=int_or_none, validate_choice=False)
    requires_experience = BooleanField("Pide experiencia previa")
    slots = IntegerField("Cupos", default=1, validators=[
        # InputRequired y no DataRequired: con DataRequired un 0 cuenta como vacío y el mensaje confunde
        InputRequired("Indica cuántas personas buscas."),
        NumberRange(1, 20, message="De 1 a 20 cupos."),
    ])

    def validate_faculty(self, field):
        if field.data is not None and db.session.get(Faculty, field.data) is None:
            raise ValidationError("Elige una facultad de la lista.")

    def validate_major(self, field):
        # Si eligió facultad, la carrera es obligatoria y tiene que ser de esa facultad
        if self.faculty.data is None:
            return
        major = db.session.get(Major, field.data) if field.data is not None else None
        if major is None or major.faculty_id != self.faculty.data:
            raise ValidationError("Elige una carrera de esa facultad.")


class ProjectDatesForm(FlaskForm):
    """Paso 3: ritmo y fechas."""

    start_date = DateField("Fecha de inicio", validators=[DataRequired("Elige la fecha de inicio.")])
    estimated_end_date = DateField("Fecha estimada de cierre", validators=[
        DataRequired("Elige la fecha estimada de cierre."),
    ])
    weekly_hours = SelectField("Dedicación semanal", choices=WEEKLY_HOURS, validate_choice=False, validators=[
        DataRequired("Elige la dedicación semanal."),
    ])
    modality = SelectField("Modalidad", choices=MODALITIES, validate_choice=False, validators=[
        DataRequired("Elige la modalidad."),
    ])

    def validate_estimated_end_date(self, field):
        if self.start_date.data and field.data and field.data < self.start_date.data:
            raise ValidationError("El cierre no puede ser antes del inicio.")

    def validate_weekly_hours(self, field):
        if field.data not in dict(WEEKLY_HOURS):
            raise ValidationError("Elige una opción de la lista.")

    def validate_modality(self, field):
        if field.data not in dict(MODALITIES):
            raise ValidationError("Elige una opción de la lista.")


class ActionForm(FlaskForm):
    """Sin campos: solo lleva el token CSRF de los botones (eliminar, ocultar, cambiar rol...)."""
