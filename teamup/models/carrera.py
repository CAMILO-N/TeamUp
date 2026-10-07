from sqlalchemy import event

from teamup.extensions import db


class Carrera(db.Model):
    idCarrera = db.Column(db.Integer, primary_key=True)
    nombreCarrera = db.Column(db.String(50), nullable=False, unique=True)


CARRERAS = [
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


@event.listens_for(Carrera.__table__, "after_create")
def _insertar_carreras(target, connection, **kw):
    """Carga las carreras justo cuando create_all() crea la tabla."""
    connection.execute(
        target.insert(), [{"nombreCarrera": nombre} for nombre in CARRERAS]
    )
