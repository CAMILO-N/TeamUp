"""Listas cerradas que comparten varios modelos y formularios: (valor guardado, texto que ve el usuario)."""

# Dedicación del proyecto y disponibilidad del perfil usan la misma lista, para poder compararlas
WEEKLY_HOURS = [
    ("1-2", "1–2 h por semana"),
    ("3-4", "3–4 h por semana"),
    ("5-6", "5–6 h por semana"),
    ("7-10", "7–10 h por semana"),
    ("10+", "Más de 10 h por semana"),
]

MODALITIES = [
    ("in_person", "Presencial"),
    ("remote", "Remota"),
    ("hybrid", "Híbrida"),
]

# Estados de un proyecto, en el orden en que avanza
PROJECT_DRAFT = "draft"
PROJECT_PENDING_REVIEW = "pending_review"
PROJECT_OPEN = "open"
PROJECT_IN_PROGRESS = "in_progress"
PROJECT_FINISHED = "finished"
PROJECT_CANCELLED = "cancelled"

PROJECT_STATUSES = [
    (PROJECT_DRAFT, "Borrador"),
    (PROJECT_PENDING_REVIEW, "En revisión"),
    (PROJECT_OPEN, "Abierto"),
    (PROJECT_IN_PROGRESS, "En curso"),
    (PROJECT_FINISHED, "Terminado"),
    (PROJECT_CANCELLED, "Cancelado"),
]

VACANCY_OPEN = "open"
VACANCY_CLOSED = "closed"

VACANCY_STATUSES = [
    (VACANCY_OPEN, "Abierta"),
    (VACANCY_CLOSED, "Cerrada"),
]

# Cola de revisión del admin: de dónde viene cada pedido y en qué quedó
REVIEW_BANNED_WORDS = "banned_words"
REVIEW_REPORT = "report"
# Un proyecto terminado pide entrar a la Vitrina
REVIEW_SHOWCASE = "showcase"

REVIEW_SOURCES = [
    (REVIEW_BANNED_WORDS, "Filtro de palabras"),
    (REVIEW_REPORT, "Reporte"),
    (REVIEW_SHOWCASE, "Vitrina"),
]

REVIEW_PENDING = "pending"
REVIEW_APPROVED = "approved"
REVIEW_REJECTED = "rejected"

REVIEW_STATUSES = [
    (REVIEW_PENDING, "Pendiente"),
    (REVIEW_APPROVED, "Aprobado"),
    (REVIEW_REJECTED, "Rechazado"),
]


def label(choices, value):
    """Texto en español de un valor de la lista; si no está, el mismo valor."""
    return dict(choices).get(value, value)
