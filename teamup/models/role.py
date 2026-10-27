from sqlalchemy import event

from teamup.extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    label = db.Column(db.String(30), nullable=False)


STUDENT = "student"
ADMIN = "admin"

# Roles iniciales: nombre interno y texto que ve el usuario
ROLES = [
    (STUDENT, "Estudiante"),
    (ADMIN, "Administrador"),
]


@event.listens_for(Role.__table__, "after_create")
def _insert_roles(target, connection, **kw):
    """Inserta los roles cuando create_all() crea la tabla."""
    connection.execute(target.insert(), [{"name": name, "label": label} for name, label in ROLES])
