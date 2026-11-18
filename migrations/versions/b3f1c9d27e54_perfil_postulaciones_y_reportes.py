"""perfil completo, postulaciones y reportes

Revision ID: b3f1c9d27e54
Revises: a8cb32dc4a37
Create Date: 2026-11-18 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3f1c9d27e54'
down_revision = 'a8cb32dc4a37'
branch_labels = None
depends_on = None


def upgrade():
    # Perfil: todo opcional, así las cuentas que ya existen no cambian
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bio', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('availability', sa.String(length=10), nullable=True))
        batch_op.add_column(sa.Column('phone', sa.String(length=15), nullable=True))
        batch_op.add_column(sa.Column('portfolio_url', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('linkedin_url', sa.String(length=200), nullable=True))

    op.create_table('skills',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user_skills',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'skill_id')
    )
    op.create_table('applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vacancy_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('decided_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['vacancy_id'], ['vacancies.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('vacancy_id', 'user_id', name='uq_applications_vacancy_user')
    )
    op.create_table('reports',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(length=20), nullable=False),
    sa.Column('detail', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_id', 'user_id', name='uq_reports_project_user')
    )


def downgrade():
    op.drop_table('reports')
    op.drop_table('applications')
    op.drop_table('user_skills')
    op.drop_table('skills')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('linkedin_url')
        batch_op.drop_column('portfolio_url')
        batch_op.drop_column('phone')
        batch_op.drop_column('availability')
        batch_op.drop_column('bio')
