from datetime import datetime

from teamup.extensions import db


class Notification(db.Model):
    """Un aviso para una persona: lo que muestra la campana."""
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    text = db.Column(db.String(300), nullable=False)
    # Dirección a la que lleva el aviso (se arma con url_for al crearlo)
    link = db.Column(db.String(200), nullable=True)
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship("User", back_populates="notifications")

    @classmethod
    def send(cls, user, text, link=None):
        """Crea un aviso para esa persona. Se guarda con el resto de los cambios (db.session.commit())."""
        notification = cls(user=user, text=text[:300], link=link)
        db.session.add(notification)
        return notification

    @classmethod
    def unread_count(cls, user):
        return cls.query.filter_by(user_id=user.id, is_read=False).count()
