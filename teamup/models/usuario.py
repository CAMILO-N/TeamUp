from flask_login import UserMixin

from teamup.extensions import db

class Usuario(UserMixin,db.Model):
    idUsuario = db.Column(db.Integer, primary_key=True)
    nombreUsuario = db.Column(db.String(25), nullable=False, unique=True)
    primerNombreUsuario = db.Column(db.String(25), nullable=False)
    segundoNombreUsuario = db.Column(db.String(25), nullable=True)
    primerApellidoUsuario = db.Column(db.String(25), nullable=False)
    segundoApellidoUsuario = db.Column(db.String(25), nullable=True)
    emailUsuario = db.Column(db.String(100), nullable=False, unique=True)
    passwordUsuario = db.Column(db.String(255), nullable=False)
    semestreUsuario = db.Column(db.Integer, nullable=False)
    carreraUsuario = db.Column(db.Integer, db.ForeignKey('carrera.idCarrera'), nullable=False)


    def get_id(self):
        return str(self.idUsuario)