"""async task tables

Revision ID: a1c2d3e4f5b6
Revises: 4c56784bb358
Create Date: 2026-11-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "a1c2d3e4f5b6"
down_revision: str | None = "4c56784bb358"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "task_outbox",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("task_name", sa.String(200), nullable=False),
        sa.Column("business_id", sa.String(200), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("payload", mysql.JSON(), nullable=False),
        sa.Column(
            "available_at",
            mysql.DATETIME(timezone=True, fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column("expires_at", mysql.DATETIME(timezone=True, fsp=6), nullable=True),
        sa.Column("published_at", mysql.DATETIME(timezone=True, fsp=6), nullable=True),
        sa.Column("cancelled_at", mysql.DATETIME(timezone=True, fsp=6), nullable=True),
        sa.Column("publish_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("max_publish_attempts", sa.Integer(), nullable=False, server_default=sa.text("10")),
        sa.Column("publish_failure", mysql.JSON(), nullable=True),
        sa.Column(
            "created_at",
            mysql.DATETIME(timezone=True, fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            mysql.DATETIME(timezone=True, fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
    )
    op.create_index(
        "idx_task_outbox_pending", "task_outbox", ["available_at", "id"], unique=False
    )

    op.create_table(
        "task_execution",
        sa.Column("id", mysql.BIGINT(unsigned=True), autoincrement=True, nullable=False),
        sa.Column("outbox_id", mysql.BIGINT(unsigned=True), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default=sa.text("'running'")),
        sa.Column("result", mysql.JSON(), nullable=True),
        sa.Column(
            "started_at",
            mysql.DATETIME(timezone=True, fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column("completed_at", mysql.DATETIME(timezone=True, fsp=6), nullable=True),
        sa.Column(
            "created_at",
            mysql.DATETIME(timezone=True, fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            mysql.DATETIME(timezone=True, fsp=6),
            server_default=sa.text("CURRENT_TIMESTAMP(6)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["outbox_id"], ["task_outbox.id"], name="fk_task_execution_outbox"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("outbox_id", "attempt", name="uq_task_execution_outbox_attempt"),
        mysql_engine="InnoDB",
    )


def downgrade() -> None:
    sa.op.drop_table("task_execution")
    sa.op.drop_index("idx_task_outbox_pending", table_name="task_outbox")
    sa.op.drop_table("task_outbox")
