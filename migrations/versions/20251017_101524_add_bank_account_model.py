"""Add BankAccount model

Revision ID: add_bank_account_model
Revises: 
Create Date: 2025-10-17 10:15:24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_bank_account_model'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create bank_accounts table
    op.create_table('bank_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('account_number', sa.String(length=100), nullable=True),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        sa.Column('balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('plaid_account_id', sa.String(length=100), nullable=True),
        sa.Column('plaid_item_id', sa.String(length=100), nullable=True),
        sa.Column('plaid_access_token', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('feeds_paused', sa.Boolean(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop bank_accounts table
    op.drop_table('bank_accounts')
