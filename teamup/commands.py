import click

from teamup.extensions import db
from teamup.models.role import ADMIN, Role
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
