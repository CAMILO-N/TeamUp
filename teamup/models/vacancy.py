from teamup.choices import APPLICATION_ACCEPTED, APPLICATION_PENDING, VACANCY_CLOSED, VACANCY_OPEN
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
    # Al borrar el rol se borran sus postulaciones
    applications = db.relationship("Application", back_populates="vacancy", cascade="all, delete-orphan",
                                   order_by="Application.created_at")

    @property
    def major_label(self):
        return self.major.name if self.major else "Cualquier carrera"

    @property
    def members(self):
        """Postulaciones aceptadas: quienes ocupan este rol."""
        return [a for a in self.applications if a.status == APPLICATION_ACCEPTED]

    @property
    def pending(self):
        return [a for a in self.applications if a.status == APPLICATION_PENDING]

    @property
    def free_slots(self):
        return max(self.slots - len(self.members), 0)

    @property
    def is_open(self):
        return self.status == VACANCY_OPEN

    def update_status(self):
        """Se cierra cuando se llenan los cupos y se vuelve a abrir si alguien se va."""
        self.status = VACANCY_OPEN if self.free_slots > 0 else VACANCY_CLOSED

    def application_of(self, user):
        """La postulación de esa persona a este rol, si existe."""
        return next((a for a in self.applications if a.user_id == user.id), None)

    def apply_blocker(self, user):
        """Por qué esa persona no puede postular a este rol; None si puede."""
        from teamup.choices import APPLICATION_WITHDRAWN, PROJECT_OPEN

        project = self.project
        if project.owner_id == user.id:
            return "No puedes postular a tu propio proyecto."
        if project.status != PROJECT_OPEN or project.is_hidden:
            return "Este proyecto ya no está buscando gente."
        if not self.is_open or self.free_slots <= 0:
            return f"El rol «{self.role_name}» ya no tiene lugares libres."
        existing = self.application_of(user)
        if existing is not None and existing.status != APPLICATION_WITHDRAWN:
            return f"Ya te postulaste al rol «{self.role_name}»."
        if self.major_id is not None and user.major_id != self.major_id:
            return f"Este rol busca a alguien de {self.major.name}."
        return None
