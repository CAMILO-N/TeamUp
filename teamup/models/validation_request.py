from datetime import datetime

from teamup.choices import (
    PROJECT_DRAFT, REVIEW_APPROVED, REVIEW_PENDING, REVIEW_REJECTED, REVIEW_SOURCES, REVIEW_STATUSES, label,
)
from teamup.extensions import db


class ValidationRequest(db.Model):
    """Un pedido en la cola del admin: un proyecto que espera revisión antes de verse en Explorar."""
    __tablename__ = "validation_requests"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    # banned_words (filtro de palabras) o report (reporte de un usuario)
    source = db.Column(db.String(20), nullable=False)
    detail = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default=REVIEW_PENDING)
    # Estado al que vuelve el proyecto si el admin lo aprueba
    return_status = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    project = db.relationship("Project", back_populates="reviews")
    reviewed_by = db.relationship("User")

    @property
    def is_pending(self):
        return self.status == REVIEW_PENDING

    @property
    def source_label(self):
        return label(REVIEW_SOURCES, self.source)

    @property
    def status_label(self):
        return label(REVIEW_STATUSES, self.status)

    def _close(self, status, admin):
        self.status = status
        self.reviewed_by = admin
        self.reviewed_at = datetime.now()

    def approve(self, admin):
        """El proyecto vuelve a su estado (publicado, en curso...)."""
        self._close(REVIEW_APPROVED, admin)
        self.project.status = self.return_status

    def reject(self, admin):
        """El proyecto vuelve a borrador: el dueño lo corrige y lo publica otra vez."""
        self._close(REVIEW_REJECTED, admin)
        self.project.status = PROJECT_DRAFT

    @classmethod
    def pending(cls):
        return cls.query.filter_by(status=REVIEW_PENDING).order_by(cls.created_at)
