from datetime import datetime

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

    @property
    def duration_days(self):
        """Días entre el inicio y el final real; None si todavía no termina."""
        if self.start_date and self.finished_at:
            return (self.finished_at - self.start_date).days
        return None
