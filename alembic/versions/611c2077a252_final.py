"""final

Revision ID: 611c2077a252
Revises: fc5efedfa4b8
Create Date: 2025-09-29 13:55:27.619448

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '611c2077a252'
down_revision = 'fc5efedfa4b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('recette',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('idRecette', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('libelle', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('debit_montant', sa.Float(), nullable=True),
    sa.Column('credit_montant', sa.Float(), nullable=True),
    sa.Column('solde', sa.Float(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['type.idType'], ),
    sa.PrimaryKeyConstraint('idRecette')
    )
    op.create_index('ix_recette_id', 'recette', ['idRecette'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_recette_id', table_name='recette')
    op.drop_table('recette')
