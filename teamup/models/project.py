from datetime import datetime

from teamup.choices import PROJECT_DRAFT
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
    def duration_days(self):
        """Días entre el inicio y el final real; None si todavía no termina."""
        if self.start_date and self.finished_at:
            return (self.finished_at - self.start_date).days
        return None
