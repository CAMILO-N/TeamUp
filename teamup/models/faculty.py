from sqlalchemy import event

from teamup.extensions import db


class Faculty(db.Model):
    __tablename__ = "faculties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    majors = db.relationship("Major", back_populates="faculty", order_by="Major.name")


# Catálogo inicial: cada facultad con sus carreras
FACULTIES = {
    "Facultad de Ingeniería y Ciencias Aplicadas": [
        "Ingeniería de Software",
        "Ingeniería en Sistemas",
        "Ingeniería Industrial",
        "Ingeniería Electrónica",
        "Ingeniería Civil",
        "Ingeniería Mecánica",
    ],
    "Facultad de Ciencias de la Salud": [
        "Medicina",
        "Enfermería",
        "Odontología",
        "Fisioterapia",
        "Nutrición y Dietética",
    ],
    "Facultad de Comunicación y Artes Audiovisuales": [
        "Cine",
        "Animación Digital",
        "Producción Audiovisual",
        "Comunicación Social",
        "Diseño Gráfico",
    ],
}


@event.listens_for(Faculty.__table__, "after_create")
def _insert_faculties(target, connection, **kw):
    """Inserta las facultades cuando create_all() crea la tabla."""
    connection.execute(target.insert(), [{"name": name} for name in FACULTIES])
