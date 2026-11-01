"""`task_outbox` 表模型：只管任务是否成功投递到 Taskiq Broker。"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Index, String, text
from sqlalchemy.dialects.mysql import BIGINT, JSON
from sqlmodel import Field, SQLModel

from backend.core.datetime import utcnow

_MAX_PUBLISH_ATTEMPTS_DEFAULT = 10


class TaskOutbox(SQLModel, table=True):
    __tablename__ = "task_outbox"  # type: ignore[assignment]
    __table_args__ = (Index("idx_task_outbox_pending", "available_at", "id"),)

    id: int | None = Field(
        default=None,
        sa_column=Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    )
    task_name: str = Field(sa_column=Column("task_name", String(200), nullable=False))
    business_id: str = Field(sa_column=Column("business_id", String(200), nullable=False))
    user_id: str | None = Field(
        default=None, sa_column=Column("user_id", String(64), nullable=True)
    )
    payload: dict = Field(sa_column=Column("payload", JSON, nullable=False))
    available_at: datetime = Field(
        sa_column=Column(
            "available_at",
            DateTime(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP(6)"),
        )
    )
    expires_at: datetime | None = Field(
        sa_column=Column("expires_at", DateTime(timezone=True), nullable=True)
    )
    published_at: datetime | None = Field(
        sa_column=Column("published_at", DateTime(timezone=True), nullable=True)
    )
    cancelled_at: datetime | None = Field(
        sa_column=Column("cancelled_at", DateTime(timezone=True), nullable=True)
    )
    publish_attempts: int = Field(default=0)
    max_publish_attempts: int = Field(default=_MAX_PUBLISH_ATTEMPTS_DEFAULT)
    publish_failure: dict | None = Field(
        sa_column=Column("publish_failure", JSON, nullable=True)
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP(6)")},
    )
    updated_at: datetime = Field(
        default_factory=utcnow,
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP(6)"),
            "onupdate": utcnow,
        },
    )


TaskOutboxEntity = TaskOutbox
