import os

from flask import Flask

from teamup.extensions import db, login_manager


def create_app():
    app = Flask(__name__)

    server = os.environ.get("DB_SERVER", "localhost")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mssql+pyodbc://@{server}/TeamUp"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )
    # Clave para firmar la cookie de sesión
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "teamup-dev-key")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."

    # Se importan los modelos para que create_all() cree sus tablas
    from teamup.models import major, user, faculty

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(user.User, int(user_id))

    with app.app_context():
        db.create_all()

    from teamup.controllers.auth import auth
    from teamup.controllers.main import main
    from teamup.controllers.profile import profile

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(profile)

    return app
