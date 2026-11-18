from flask_login import UserMixin

from teamup.choices import APPLICATION_ACCEPTED, PROJECT_FINISHED, WEEKLY_HOURS, label
from teamup.extensions import db
from teamup.models.role import ADMIN
from teamup.models.skill import user_skills


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

    # Perfil (todo opcional): se completa en "Mi perfil"
    bio = db.Column(db.Text, nullable=True)
    # Horas por semana, de la misma lista que la dedicación de los proyectos
    availability = db.Column(db.String(10), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    portfolio_url = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)

    major = db.relationship("Major")
    role = db.relationship("Role")
    # Al borrar la cuenta se borran también sus proyectos
    projects = db.relationship("Project", back_populates="owner", cascade="all, delete-orphan",
                               order_by="Project.created_at.desc()")
    skills = db.relationship("Skill", secondary=user_skills, order_by="Skill.name")
    applications = db.relationship("Application", back_populates="user", cascade="all, delete-orphan",
                                   order_by="Application.created_at.desc()")
    reports = db.relationship("Report", back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan",
                                    order_by="Notification.created_at.desc()", lazy="dynamic")

    @property
    def initials(self):
        """Iniciales para el círculo del usuario, como "CN"."""
        return (self.first_name[:1] + self.last_name[:1]).upper()

    @property
    def is_admin(self):
        return self.role.name == ADMIN

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def availability_label(self):
        return label(WEEKLY_HOURS, self.availability)

    @property
    def joined_projects(self):
        """Proyectos públicos donde fue aceptado (sin contar los que creó)."""
        return [a.project for a in self.applications if a.status == APPLICATION_ACCEPTED and a.project.is_public]

    @property
    def public_projects(self):
        """Proyectos públicos que creó."""
        return [p for p in self.projects if p.is_public]

    @property
    def finished_count(self):
        """Proyectos realizados: los terminados que creó o en los que participó. Se cuentan, no se guardan."""
        return sum(1 for p in self.public_projects + self.joined_projects if p.status == PROJECT_FINISHED)
