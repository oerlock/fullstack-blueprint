"""任务投递箱的输入与查询 DTO。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

# 投递侧以该参数名附加 outbox_id，payload 中不允许同名键
RESERVED_PAYLOAD_KEYS = frozenset({"outbox_id"})


class CreateTaskOutboxDTO(BaseModel):
    """创建任务入参，在业务事务内随业务一起提交。"""

    model_config = ConfigDict(frozen=True)

    task_name: str = Field(min_length=1, max_length=200)
    business_id: str = Field(min_length=1, max_length=200)
    user_id: str | None = Field(default=None, max_length=64)
    payload: dict = Field(default_factory=dict)
    available_at: datetime | None = None
    expires_at: datetime | None = None
    max_publish_attempts: int = Field(default=10, ge=1)

    @model_validator(mode="after")
    def validate_rules(self) -> "CreateTaskOutboxDTO":
        if not self.task_name.strip() or not self.business_id.strip():
            raise ValueError("task_name / business_id 不能为空白")
        if RESERVED_PAYLOAD_KEYS & set(self.payload):
            raise ValueError(f"payload 不允许包含保留键: {sorted(RESERVED_PAYLOAD_KEYS)}")
        if (
            self.available_at is not None
            and self.expires_at is not None
            and self.expires_at <= self.available_at
        ):
            raise ValueError("expires_at 必须晚于 available_at")
        return self
