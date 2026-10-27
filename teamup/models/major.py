from sqlalchemy import event

from teamup.extensions import db


class Major(db.Model):
    __tablename__ = "majors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


MAJORS = [
    "Ingeniería de Sistemas",
    "Ingeniería de Software",
    "Ingeniería Industrial",
    "Ingeniería Electrónica",
    "Ingeniería Civil",
    "Ingeniería Mecánica",
    "Administración de Empresas",
    "Contaduría Pública",
    "Economía",
    "Derecho",
    "Psicología",
    "Medicina",
    "Arquitectura",
    "Diseño Gráfico",
    "Comunicación Social",
]


@event.listens_for(Major.__table__, "after_create")
def _insert_majors(target, connection, **kw):
    """Inserta las carreras cuando create_all() crea la tabla."""
    connection.execute(target.insert(), [{"name": name} for name in MAJORS])


def major_choices():
    """Opciones del selector de carrera, ordenadas por nombre."""
    return [(major.id, major.name) for major in Major.query.order_by(Major.name).all()]
