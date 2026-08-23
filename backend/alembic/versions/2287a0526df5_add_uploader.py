"""add uploader

Revision ID: 2287a0526df5
Revises: dc1fe517afdd
Create Date: 2026-08-08 02:06:16.520323
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.

revision: str = "2287a0526df5"
down_revision: str | Sequence[str] | None = "dc1fe517afdd"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "clips",
        sa.Column(
            "uploader",
            sa.String(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "clips",
        "uploader",
    )