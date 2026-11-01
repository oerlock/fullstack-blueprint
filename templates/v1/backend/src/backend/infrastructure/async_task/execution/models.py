"""`task_execution` 表模型：每次实际执行尝试一条记录。"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.mysql import BIGINT, JSON
from sqlmodel import Field, SQLModel

from backend.core.datetime import utcnow
from backend.infrastructure.async_task.execution.schemas import TaskExecutionStatus


class TaskExecution(SQLModel, table=True):
    __tablename__ = "task_execution"  # type: ignore[assignment]
    __table_args__ = (
        UniqueConstraint("outbox_id", "attempt", name="uq_task_execution_outbox_attempt"),
    )

    id: int | None = Field(
        default=None,
        sa_column=Column("id", BIGINT(unsigned=True), primary_key=True, autoincrement=True),
    )
    outbox_id: int = Field(
        sa_column=Column(
            "outbox_id", BIGINT(unsigned=True), ForeignKey("task_outbox.id"), nullable=False
        )
    )
    attempt: int
    status: str = Field(
        default=TaskExecutionStatus.RUNNING.value,
        sa_column=Column("status", String(20), nullable=False),
    )
    result: dict | None = Field(sa_column=Column("result", JSON, nullable=True))
    started_at: datetime = Field(
        default_factory=utcnow,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP(6)")},
    )
    completed_at: datetime | None = Field(
        sa_column=Column("completed_at", DateTime(timezone=True), nullable=True)
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


TaskExecutionEntity = TaskExecution
