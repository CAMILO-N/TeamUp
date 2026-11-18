from datetime import datetime

from teamup.choices import REPORT_REASONS, label
from teamup.extensions import db


class Report(db.Model):
    """Un reporte de un usuario sobre un proyecto. Con el primero, el proyecto pasa a la cola del admin."""
    __tablename__ = "reports"
    # Cada persona reporta un mismo proyecto una sola vez
    __table_args__ = (db.UniqueConstraint("project_id", "user_id", name="uq_reports_project_user"),)

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = db.Column(db.String(20), nullable=False)
    detail = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    project = db.relationship("Project", back_populates="reports")
    user = db.relationship("User", back_populates="reports")

    @property
    def reason_label(self):
        return label(REPORT_REASONS, self.reason)

    def summary(self):
        """Una línea para la cola del admin: "@usuario: motivo (detalle)"."""
        text = f"@{self.user.username}: {self.reason_label}"
        return f"{text} ({self.detail})" if self.detail else text
