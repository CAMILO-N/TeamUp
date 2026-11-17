from teamup.choices import VACANCY_OPEN
from teamup.extensions import db


class Vacancy(db.Model):
    """Un rol que busca un proyecto. Quién lo ocupa sale de las postulaciones aceptadas."""

    __tablename__ = "vacancies"
    __table_args__ = (db.CheckConstraint("slots >= 1", name="ck_vacancies_slots_positive"),)

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    role_name = db.Column(db.String(60), nullable=False)
    # Vacío = cualquier carrera
    major_id = db.Column(db.Integer, db.ForeignKey("majors.id"), nullable=True)
    requires_experience = db.Column(db.Boolean, nullable=False, default=False)
    slots = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(20), nullable=False, default=VACANCY_OPEN)

    project = db.relationship("Project", back_populates="vacancies")
    major = db.relationship("Major")

    @property
    def major_label(self):
        return self.major.name if self.major else "Cualquier carrera"
