"""vitrina con aprobacion del admin

Revision ID: a8cb32dc4a37
Revises: 1e4b50739fc2
Create Date: 2026-11-18 10:42:08.167295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a8cb32dc4a37'
down_revision = '1e4b50739fc2'
branch_labels = None
depends_on = None


def upgrade():
    # Los proyectos que ya existen empiezan fuera de la Vitrina
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('in_showcase', sa.Boolean(), nullable=False, server_default=sa.false()))
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.alter_column('in_showcase', server_default=None)

    # Los que ya estaban terminados piden entrar: quedan en la cola del admin
    op.execute("""
        INSERT INTO validation_requests (project_id, source, detail, status, return_status, created_at)
        SELECT id, 'showcase', 'Terminado: pide entrar a la Vitrina', 'pending', 'finished', NOW()
        FROM projects WHERE status = 'finished'
    """)


def downgrade():
    op.execute("DELETE FROM validation_requests WHERE source = 'showcase'")
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_column('in_showcase')
