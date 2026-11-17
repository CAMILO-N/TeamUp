import click

from teamup.extensions import db
from teamup.models.faculty import FACULTIES, Faculty
from teamup.models.major import Major
from teamup.models.role import ADMIN, ROLES, Role
from teamup.models.user import User


def register_commands(app):
    @app.cli.command("create-admin")
    @click.argument("username")
    def create_admin(username):
        """Convierte en administrador a un usuario ya registrado."""
        user = User.query.filter_by(username=username.lower()).first()
        if user is None:
            raise click.ClickException(f"No existe el usuario @{username}. Primero regístrate en la página.")

        user.role = Role.query.filter_by(name=ADMIN).one()
        db.session.commit()
        click.echo(f"@{username} ahora es administrador.")

    @app.cli.command("seed")
    def seed():
        """Carga los datos iniciales que falten: roles, facultades y carreras. No duplica nada."""
        added = 0

        for name, label in ROLES:
            if Role.query.filter_by(name=name).first() is None:
                db.session.add(Role(name=name, label=label))
                added += 1

        for faculty_name, major_names in FACULTIES.items():
            faculty = Faculty.query.filter_by(name=faculty_name).first()
            if faculty is None:
                faculty = Faculty(name=faculty_name)
                db.session.add(faculty)
                added += 1
            for major_name in major_names:
                if Major.query.filter_by(name=major_name).first() is None:
                    db.session.add(Major(name=major_name, faculty=faculty))
                    added += 1

        db.session.commit()
        click.echo(f"Datos iniciales listos ({added} registros nuevos).")
