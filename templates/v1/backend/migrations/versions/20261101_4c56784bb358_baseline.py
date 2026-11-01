"""baseline

Revision ID: 4c56784bb358
Revises:
Create Date: 2026-11-01 21:50:30.065123

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "4c56784bb358"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
