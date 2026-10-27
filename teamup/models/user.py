from flask_login import UserMixin

from teamup.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    first_name = db.Column(db.String(25), nullable=False)
    middle_name = db.Column(db.String(25), nullable=True)
    last_name = db.Column(db.String(25), nullable=False)
    second_last_name = db.Column(db.String(25), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    # Texto y no número: hay cédulas que empiezan con 0
    id_number = db.Column(db.String(10), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    major_id = db.Column(db.Integer, db.ForeignKey("majors.id"), nullable=False)
