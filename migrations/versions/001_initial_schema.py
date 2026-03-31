"""Initial certificate schema migration

Revision ID: 001
Revises: 
Create Date: 2026-02-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'issued_certificates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('serial', sa.String(), nullable=True),
        sa.Column('common_name', sa.String(), nullable=False),
        sa.Column('cert_type', sa.String(), nullable=True),
        sa.Column('cert_pem', sa.Text(), nullable=False),
        sa.Column('issued_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoke_reason', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_issued_certificates_serial'), 'issued_certificates', ['serial'], unique=True)
    
    op.create_table(
        'api_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username')
    )

def downgrade() -> None:
    op.drop_table('api_users')
    op.drop_index(op.f('ix_issued_certificates_serial'), table_name='issued_certificates')
    op.drop_table('issued_certificates')
