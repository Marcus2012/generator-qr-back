"""rename pdf_url to blob_name

Revision ID: 74c60b58db3f
Revises: c5da1e63bf3d
Create Date: 2026-09-06 23:50:55.100326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '74c60b58db3f'
down_revision: Union[str, None] = 'c5da1e63bf3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'qr_codes', 'pdf_url',
        new_column_name='blob_name',
        existing_type=sa.String(length=1024),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'qr_codes', 'blob_name',
        new_column_name='pdf_url',
        existing_type=sa.String(length=1024),
        existing_nullable=False,
    )
