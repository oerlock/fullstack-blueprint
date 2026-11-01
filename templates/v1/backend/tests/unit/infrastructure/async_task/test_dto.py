"""CreateTaskOutboxDTO 校验单元测试。"""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from backend.infrastructure.async_task.outbox.dto import CreateTaskOutboxDTO

_NOW = datetime(2026, 11, 1, tzinfo=UTC)


def test_valid_minimal():
    dto = CreateTaskOutboxDTO(task_name="generate_report", business_id="report-1")
    assert dto.payload == {}
    assert dto.max_publish_attempts == 10
    assert dto.available_at is None


def test_blank_task_name_rejected():
    with pytest.raises(ValidationError):
        CreateTaskOutboxDTO(task_name="  ", business_id="b")


def test_blank_business_id_rejected():
    with pytest.raises(ValidationError):
        CreateTaskOutboxDTO(task_name="t", business_id="")


def test_payload_with_reserved_key_rejected():
    with pytest.raises(ValidationError, match="outbox_id"):
        CreateTaskOutboxDTO(task_name="t", business_id="b", payload={"outbox_id": 1})


def test_expires_at_must_be_after_available_at():
    with pytest.raises(ValidationError):
        CreateTaskOutboxDTO(
            task_name="t",
            business_id="b",
            available_at=_NOW,
            expires_at=_NOW,
        )
    with pytest.raises(ValidationError):
        CreateTaskOutboxDTO(
            task_name="t",
            business_id="b",
            available_at=_NOW,
            expires_at=_NOW + timedelta(seconds=-1),
        )


def test_expires_at_only_is_allowed():
    dto = CreateTaskOutboxDTO(task_name="t", business_id="b", expires_at=_NOW + timedelta(hours=1))
    assert dto.expires_at is not None


def test_max_publish_attempts_minimum_one():
    with pytest.raises(ValidationError):
        CreateTaskOutboxDTO(task_name="t", business_id="b", max_publish_attempts=0)
