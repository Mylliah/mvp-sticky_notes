"""add_read_date_to_assignment_remove_from_note

Revision ID: 054f0b330c56
Revises: 653833f10fe3
Create Date: 2025-10-18 19:12:24.864250

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '054f0b330c56'
down_revision = '653833f10fe3'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter la colonne read_date à la table assignments
    op.add_column('assignments', sa.Column('read_date', sa.DateTime(), nullable=True))
    
    # Supprimer la colonne read_date de la table notes
    op.drop_column('notes', 'read_date')


def downgrade():
    # Remettre la colonne read_date dans la table notes
    op.add_column('notes', sa.Column('read_date', sa.DateTime(), nullable=True))
    
    # Supprimer la colonne read_date de la table assignments
    op.drop_column('assignments', 'read_date')
