from datetime import datetime

from sqlalchemy import or_

from teamup.choices import (
    MODALITIES, PROJECT_DRAFT, PROJECT_FINISHED, PROJECT_IN_PROGRESS, PROJECT_OPEN, PROJECT_STATUSES,
    WEEKLY_HOURS, label,
)
from teamup.extensions import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    # Descripción corta para las tarjetas de Explorar
    summary = db.Column(db.String(200), nullable=True)
    description = db.Column(db.Text, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Opcionales en la base porque un borrador se llena paso a paso;
    # al publicar, el servidor revisa que estén completos
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    modality = db.Column(db.String(20), nullable=True)
    weekly_hours = db.Column(db.String(10), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    estimated_end_date = db.Column(db.Date, nullable=True)
    # Cuándo terminó de verdad; la duración se calcula, no se guarda
    finished_at = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(20), nullable=False, default=PROJECT_DRAFT)
    # Un proyecto oculto no aparece en Explorar, pero no se borra
    is_hidden = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    owner = db.relationship("User", back_populates="projects")
    category = db.relationship("Category")
    # Al borrar el proyecto se borran sus vacantes
    vacancies = db.relationship("Vacancy", back_populates="project", cascade="all, delete-orphan",
                                order_by="Vacancy.id")

    @property
    def is_draft(self):
        return self.status == PROJECT_DRAFT

    @property
    def is_public(self):
        """Lo puede ver cualquiera: publicado y no oculto por el admin."""
        return self.status in (PROJECT_OPEN, PROJECT_IN_PROGRESS, PROJECT_FINISHED) and not self.is_hidden

    @property
    def status_label(self):
        return label(PROJECT_STATUSES, self.status)

    @property
    def modality_label(self):
        return label(MODALITIES, self.modality)

    @property
    def weekly_hours_label(self):
        return label(WEEKLY_HOURS, self.weekly_hours)

    def missing_for_publish(self):
        """Lo que falta para publicar, en el orden de los pasos. Vacío = se puede publicar."""
        missing = []
        if not (self.title and self.summary and self.description and self.category_id):
            missing.append("la información del paso 1")
        if not self.vacancies:
            missing.append("al menos un rol")
        if not (self.start_date and self.estimated_end_date and self.weekly_hours and self.modality):
            missing.append("las fechas, la dedicación y la modalidad")
        return missing

    def finish(self, day):
        """Marca el proyecto como terminado en esa fecha. Devuelve un mensaje si no se puede."""
        if self.status not in (PROJECT_OPEN, PROJECT_IN_PROGRESS):
            return "Solo se puede terminar un proyecto publicado."
        if self.start_date and day < self.start_date:
            return "No se puede terminar antes de la fecha de inicio."
        self.status = PROJECT_FINISHED
        self.finished_at = day
        return None

    @classmethod
    def search(cls, category_id=None, faculty_id=None, major_id=None, modality=None, weekly_hours=None):
        """Proyectos de Explorar (publicados y no ocultos), con filtros opcionales.

        Por carrera o facultad salen los que tienen un rol abierto para esa carrera
        o para cualquier carrera, porque esa persona también puede postularse ahí."""
        from teamup.choices import VACANCY_OPEN
        from teamup.models.major import Major
        from teamup.models.vacancy import Vacancy

        query = cls.query.filter_by(status=PROJECT_OPEN, is_hidden=False)
        if category_id:
            query = query.filter(cls.category_id == category_id)
        if modality:
            query = query.filter(cls.modality == modality)
        if weekly_hours:
            query = query.filter(cls.weekly_hours == weekly_hours)
        if major_id:
            query = query.filter(cls.vacancies.any(
                (Vacancy.status == VACANCY_OPEN) & or_(Vacancy.major_id == major_id, Vacancy.major_id.is_(None))))
        elif faculty_id:
            query = query.filter(cls.vacancies.any(
                (Vacancy.status == VACANCY_OPEN)
                & or_(Vacancy.major_id.is_(None), Vacancy.major.has(Major.faculty_id == faculty_id))))
        return query.order_by(cls.created_at.desc())

    @property
    def duration_days(self):
        """Días entre el inicio y el final real; None si todavía no termina."""
        if self.start_date and self.finished_at:
            return (self.finished_at - self.start_date).days
        return None
