from datetime import datetime

from teamup.choices import (
    APPLICATION_ACCEPTED, APPLICATION_PENDING, APPLICATION_REJECTED, APPLICATION_STATUSES, APPLICATION_WITHDRAWN,
    label,
)
from teamup.extensions import db


class Application(db.Model):
    """Una postulación de una persona a una vacante. Las aceptadas son el equipo del proyecto."""
    __tablename__ = "applications"
    # Una persona no puede postular dos veces a la misma vacante
    __table_args__ = (db.UniqueConstraint("vacancy_id", "user_id", name="uq_applications_vacancy_user"),)

    id = db.Column(db.Integer, primary_key=True)
    vacancy_id = db.Column(db.Integer, db.ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=APPLICATION_PENDING)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    decided_at = db.Column(db.DateTime, nullable=True)

    vacancy = db.relationship("Vacancy", back_populates="applications")
    user = db.relationship("User", back_populates="applications")

    @property
    def project(self):
        return self.vacancy.project

    @property
    def status_label(self):
        return label(APPLICATION_STATUSES, self.status)

    @property
    def is_pending(self):
        return self.status == APPLICATION_PENDING

    @property
    def is_accepted(self):
        return self.status == APPLICATION_ACCEPTED

    @property
    def is_withdrawn(self):
        return self.status == APPLICATION_WITHDRAWN

    @property
    def can_withdraw(self):
        """La persona puede retirarse mientras espera o, si ya está en el equipo, mientras el proyecto no termine."""
        return self.is_pending or (self.is_accepted and not self.project.is_finished)

    def accept(self):
        """El dueño acepta. Vuelve a contar los cupos en el servidor. Devuelve un mensaje si no se puede."""
        from teamup.models.vacancy import Vacancy

        if not self.is_pending:
            return "Esa postulación ya fue decidida."
        # Se bloquea la vacante para que dos aceptaciones al mismo tiempo no pasen del cupo
        vacancy = db.session.query(Vacancy).filter_by(id=self.vacancy_id).with_for_update().one()
        if vacancy.free_slots <= 0:
            return f"El rol «{vacancy.role_name}» ya no tiene lugares libres."
        self._decide(APPLICATION_ACCEPTED)
        vacancy.update_status()
        return None

    def reject(self):
        if not self.is_pending:
            return "Esa postulación ya fue decidida."
        self._decide(APPLICATION_REJECTED)
        return None

    def withdraw(self):
        """La persona se retira. Si estaba en el equipo, su lugar vuelve a quedar libre."""
        if not self.can_withdraw:
            return "Esa postulación ya no se puede retirar."
        was_accepted = self.is_accepted
        self._decide(APPLICATION_WITHDRAWN)
        if was_accepted:
            self.vacancy.update_status()
        return None

    def _decide(self, status):
        self.status = status
        self.decided_at = datetime.now()
