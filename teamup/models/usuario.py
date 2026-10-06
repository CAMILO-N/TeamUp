
from teamup.extensions import db


class Usuario(db.Model):
    idUsuario = db.Column(db.Integer, primary_key=True)
    nombreUsuario = db.Column(db.String(25), nullable=False)
    apellidoUsuario = db.Column(db.String(25), nullable=False)
    emailUsuario = db.Column(db.String(100), nullable=False, unique=True)
    passwordUsuario = db.Column(db.String(255), nullable=False)
    semestreUsuario = db.Column(db.Integer, nullable=False)
    carreraUsuario = db.Column(db.Integer, db.ForeignKey('carrera.idCarrera'), nullable=False)