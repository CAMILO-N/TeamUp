import os

from dotenv import load_dotenv
from flask import Flask, render_template

from teamup.extensions import db, login_manager, migrate


def database_uri():
    """Dirección de la base de Neon (PostgreSQL), tomada de DATABASE_URL."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url:
        raise RuntimeError("Falta DATABASE_URL: ponla en el archivo .env (o en las variables de Vercel).")

    # SQLAlchemy necesita saber que el driver es psycopg
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


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
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Inicia sesión para continuar."

    # Se importan los modelos para que Flask-Migrate conozca sus tablas
    from teamup.models import (
        application, banned_word, category, faculty, major, notification, project, report, role, skill, user,
        vacancy, validation_request,
    )

    @login_manager.user_loader
    def load_user(user_id):
        # Si la cuenta fue desactivada, la sesión deja de valer
        found = db.session.get(user.User, int(user_id))
        return found if found and found.is_active else None

    from teamup.controllers.admin import admin
    from teamup.controllers.applications import applications
    from teamup.controllers.auth import auth
    from teamup.controllers.main import main
    from teamup.controllers.notifications import notifications
    from teamup.controllers.profile import profile
    from teamup.controllers.projects import projects
    from teamup.controllers.reports import reports

    app.register_blueprint(admin)
    app.register_blueprint(applications)
    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(notifications)
    app.register_blueprint(profile)
    app.register_blueprint(projects)
    app.register_blueprint(reports)

    @app.context_processor
    def unread_notifications():
        """Cuántos avisos sin leer tiene el usuario: lo muestra la campana en todas las páginas."""
        from flask_login import current_user

        if current_user.is_authenticated:
            return {"unread_notifications": notification.Notification.unread_count(current_user)}
        return {"unread_notifications": 0}

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("403.html"), 403

    from teamup.commands import register_commands
    register_commands(app)

    return app
