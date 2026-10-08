import os

from flask import Flask
from teamup.extensions import db, login_manager


def create_app():

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mssql+pyodbc://@MSI\\SQLEXPRESS/TeamUp"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes"
    "&TrustServerCertificate=yes")
    # Clave con la que Flask firma la cookie de sesión
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "teamup-clave-de-desarrollo")

    db.init_app(app)
    login_manager.init_app(app)

    
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."

    from teamup.models import carrera, usuario

    @login_manager.user_loader
    def cargar_usuario(id_usuario):
      
        return db.session.get(usuario.Usuario, int(id_usuario))

    with app.app_context():
        db.create_all()

    # Controladores
    from teamup.controllers.auth import auth
    from teamup.controllers.perfil import perfil
    from teamup.controllers.principal import principal

    app.register_blueprint(auth)
    app.register_blueprint(principal)
    app.register_blueprint(perfil)

    return app
