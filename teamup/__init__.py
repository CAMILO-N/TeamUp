import os

from dotenv import load_dotenv
from flask import Flask, render_template

from teamup.extensions import db, login_manager


def database_uri():
    """Base de Neon (PostgreSQL) si hay DATABASE_URL; si no, el SQL Server local."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        # SQLAlchemy necesita saber que el driver es psycopg
        for prefix in ("postgresql://", "postgres://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    server = os.environ.get("DB_SERVER", "localhost")
    return (
        f"mssql+pyodbc://@{server}/TeamUp"
        "?driver=ODBC+Driver+17+for+SQL+Server"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )


def create_app():
    # Lee el archivo .env si existe (no se sube a Git)
    load_dotenv()

    app = Flask(__name__)

    # Solo se aceptan correos de este dominio
    app.config["ALLOWED_EMAIL_DOMAIN"] = "udla.edu.ec"

    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri()
    # Neon apaga la base cuando nadie la usa: se revisa la conexión antes de usarla
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

    # Clave para firmar la cookie de sesión. En Vercel es obligatoria
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key and os.environ.get("VERCEL"):
        raise RuntimeError("Falta la variable SECRET_KEY en Vercel.")
    app.config["SECRET_KEY"] = secret_key or "teamup-dev-key"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."

    # Se importan los modelos para que create_all() cree sus tablas
    from teamup.models import faculty, major, project, role, user

    @login_manager.user_loader
    def load_user(user_id):
        # Si la cuenta fue desactivada, la sesión deja de valer
        found = db.session.get(user.User, int(user_id))
        return found if found and found.is_active else None

    with app.app_context():
        db.create_all()

    from teamup.controllers.admin import admin
    from teamup.controllers.auth import auth
    from teamup.controllers.main import main
    from teamup.controllers.profile import profile
    from teamup.controllers.projects import projects

    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(profile)
    app.register_blueprint(projects)

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    from teamup.commands import register_commands
    register_commands(app)

    return app
