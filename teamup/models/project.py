from datetime import datetime

from sqlalchemy import or_

from teamup.choices import (
    MODALITIES, PROJECT_DRAFT, PROJECT_FINISHED, PROJECT_IN_PROGRESS, PROJECT_OPEN, PROJECT_PENDING_REVIEW,
    PROJECT_STATUSES, REVIEW_BANNED_WORDS, REVIEW_PENDING, REVIEW_REJECTED, REVIEW_SHOWCASE, WEEKLY_HOURS, label,
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
    # Un terminado entra a la Vitrina solo cuando el admin lo aprueba
    in_showcase = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    owner = db.relationship("User", back_populates="projects")
    category = db.relationship("Category")
    # Al borrar el proyecto se borran sus vacantes
    vacancies = db.relationship("Vacancy", back_populates="project", cascade="all, delete-orphan",
                                order_by="Vacancy.id")
    # Pedidos de revisión del admin (filtro de palabras o reportes)
    reviews = db.relationship("ValidationRequest", back_populates="project", cascade="all, delete-orphan",
                              passive_deletes=True, order_by="ValidationRequest.created_at.desc()")

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
    def is_in_review(self):
        return self.status == PROJECT_PENDING_REVIEW

    @property
    def is_finished(self):
        return self.status == PROJECT_FINISHED

    @property
    def showcase_status(self):
        """Dónde está un terminado respecto a la Vitrina: approved, pending, rejected o None."""
        if self.in_showcase:
            return "approved"
        request = next((r for r in self.reviews if r.source == REVIEW_SHOWCASE), None)
        if request is None:
            return None
        return "rejected" if request.status == REVIEW_REJECTED else "pending" if request.is_pending else None

    @property
    def last_review(self):
        return self.reviews[0] if self.reviews else None

    def send_to_review(self, source, detail):
        """Manda el proyecto a la cola del admin: deja de verse en Explorar hasta que lo aprueben.

        source es REVIEW_BANNED_WORDS o REVIEW_REPORT. Si ya hay un pedido pendiente
        del mismo origen, se actualiza ese en lugar de crear otro."""
        from teamup.models.validation_request import ValidationRequest

        request = next((r for r in self.reviews if r.status == REVIEW_PENDING and r.source == source), None)
        if request is None:
            # Al aprobarlo vuelve a como estaba; un borrador que se publica vuelve como abierto
            back_to = PROJECT_OPEN if self.status in (PROJECT_DRAFT, PROJECT_PENDING_REVIEW) else self.status
            request = ValidationRequest(source=source, return_status=back_to)
            self.reviews.insert(0, request)
        request.detail = detail
        self.status = PROJECT_PENDING_REVIEW
        return request

    def banned_words(self):
        """Palabras del filtro que aparecen en el título, los resúmenes o los roles."""
        from teamup.models.banned_word import BannedWord

        texts = [self.title, self.summary, self.description] + [v.role_name for v in self.vacancies]
        return BannedWord.find_in("\n".join(t for t in texts if t))

    def check_banned_words(self):
        """Si el proyecto usa palabras del filtro, lo manda a revisión. Devuelve True si lo mandó."""
        words = self.banned_words()
        if words:
            self.send_to_review(REVIEW_BANNED_WORDS, "Palabras marcadas: " + ", ".join(words))
        return bool(words)

    @property
    def total_slots(self):
        return sum(vacancy.slots for vacancy in self.vacancies)

    @property
    def initials(self):
        """Iniciales del proyecto para su círculo: "Punto de fuga" queda "PF" (se saltan las palabras cortas)."""
        words = [word for word in self.title.split() if len(word) > 2] or self.title.split()
        return "".join(word[0] for word in words[:2]).upper()

    def start(self):
        """El equipo ya arrancó: deja de buscar gente en Explorar. Devuelve un mensaje si no se puede."""
        if self.status != PROJECT_OPEN:
            return "Solo se puede arrancar un proyecto abierto."
        self.status = PROJECT_IN_PROGRESS
        return None

    def reopen(self):
        """Un proyecto en curso vuelve a buscar gente (por ejemplo, si alguien se fue)."""
        if self.status != PROJECT_IN_PROGRESS:
            return "Solo un proyecto en curso puede volver a buscar gente."
        self.status = PROJECT_OPEN
        return None

    def finish(self, day):
        """Marca el proyecto como terminado en esa fecha. Devuelve un mensaje si no se puede."""
        if self.status not in (PROJECT_OPEN, PROJECT_IN_PROGRESS):
            return "Solo se puede terminar un proyecto publicado."
        if self.start_date and day < self.start_date:
            return "No se puede terminar antes de la fecha de inicio."
        self.status = PROJECT_FINISHED
        self.finished_at = day
        self.request_showcase()
        return None

    def request_showcase(self):
        """Pide al admin que el proyecto terminado entre a la Vitrina. No cambia su estado."""
        from teamup.models.validation_request import ValidationRequest

        self.reviews.insert(0, ValidationRequest(source=REVIEW_SHOWCASE, return_status=PROJECT_FINISHED,
                                                 detail="Terminado: pide entrar a la Vitrina"))

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

    @classmethod
    def showcase(cls):
        """Proyectos de la Vitrina: terminados, aprobados por el admin y no ocultos, del más reciente al más antiguo."""
        return (cls.query.filter_by(status=PROJECT_FINISHED, in_showcase=True, is_hidden=False)
                .order_by(cls.finished_at.desc()))

    @property
    def duration_days(self):
        """Días entre el inicio y el final real; None si todavía no termina."""
        if self.start_date and self.finished_at:
            return (self.finished_at - self.start_date).days
        return None
