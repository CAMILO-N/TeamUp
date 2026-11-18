import re
import unicodedata
from datetime import datetime

from teamup.extensions import db


def normalize(text):
    """Minúsculas y sin tildes, para que "Párrafo" y "parrafo" cuenten igual."""
    text = unicodedata.normalize("NFD", (text or "").lower())
    return "".join(char for char in text if unicodedata.category(char) != "Mn")


class BannedWord(db.Model):
    """Palabras del filtro: un proyecto que las usa pasa por la revisión del admin."""
    __tablename__ = "banned_words"

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(40), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    @classmethod
    def find_in(cls, text):
        """Las palabras del filtro que aparecen en el texto, como palabra completa ("ser" no marca "serie")."""
        clean = normalize(text)
        return [banned.word for banned in cls.query.order_by(cls.word).all()
                if re.search(r"\b" + re.escape(normalize(banned.word)) + r"\b", clean)]
