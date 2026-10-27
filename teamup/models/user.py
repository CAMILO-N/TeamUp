from flask_login import UserMixin

from teamup.extensions import db
from teamup.models.role import ADMIN


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    first_name = db.Column(db.String(25), nullable=False)
    middle_name = db.Column(db.String(25), nullable=True)
    last_name = db.Column(db.String(25), nullable=False)
    second_last_name = db.Column(db.String(25), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    # Texto y no número: hay cédulas que empiezan con 0
    id_number = db.Column(db.String(10), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey("majors.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    # Flask-Login no deja entrar a una cuenta desactivada
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    major = db.relationship("Major")
    role = db.relationship("Role")
    # Al borrar la cuenta se borran también sus proyectos
    projects = db.relationship("Project", back_populates="owner", cascade="all, delete-orphan",
                               order_by="Project.created_at.desc()")

    @property
    def is_admin(self):
        return self.role.name == ADMIN
