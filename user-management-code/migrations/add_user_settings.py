"""Add user settings and profile fields

Revision ID: add_user_settings
Revises: previous_migration_id
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = 'add_user_settings'
down_revision = 'previous_migration_id'  # Replace with your actual previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    """Add user settings and profile columns to users table."""
    
    # Add profile fields
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    
    # Add settings fields
    op.add_column('users', sa.Column('language', sa.String(10), nullable=False, server_default='en'))
    op.add_column('users', sa.Column('timezone', sa.String(50), nullable=False, server_default='UTC'))
    op.add_column('users', sa.Column('date_format', sa.String(20), nullable=False, server_default='MM/DD/YYYY'))
    op.add_column('users', sa.Column('currency_format', sa.String(10), nullable=False, server_default='USD'))
    
    # Add notification preferences
    op.add_column('users', sa.Column('email_notifications', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('dashboard_notifications', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('marketing_emails', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add updated_at column if it doesn't exist
    # Check if column exists first to avoid conflicts
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'updated_at' not in columns:
        op.add_column('users', sa.Column('updated_at', sa.DateTime(), 
                                       nullable=False, 
                                       server_default=sa.text('CURRENT_TIMESTAMP')))


def downgrade():
    """Remove user settings and profile columns from users table."""
    
    # Remove settings fields
    op.drop_column('users', 'marketing_emails')
    op.drop_column('users', 'dashboard_notifications')
    op.drop_column('users', 'email_notifications')
    op.drop_column('users', 'currency_format')
    op.drop_column('users', 'date_format')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'language')
    
    # Remove profile fields
    op.drop_column('users', 'phone')
    
    # Note: We don't drop updated_at as it might be used by other parts of the application