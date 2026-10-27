from sqlalchemy import event, select

from teamup.extensions import db
from teamup.models.faculty import FACULTIES, Faculty


class Major(db.Model):
    __tablename__ = "majors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)

    faculty = db.relationship("Faculty", back_populates="majors")


@event.listens_for(Major.__table__, "after_create")
def _insert_majors(target, connection, **kw):
    """Inserta las carreras de cada facultad cuando create_all() crea la tabla."""
    faculty_ids = dict(connection.execute(select(Faculty.name, Faculty.id)).all())
    connection.execute(target.insert(), [
        {"name": major, "faculty_id": faculty_ids[faculty]}
        for faculty, majors in FACULTIES.items()
        for major in majors
    ])


def major_choices():
    """Opciones del selector de carrera, ordenadas por nombre."""
    return [(major.id, major.name) for major in Major.query.order_by(Major.name).all()]
