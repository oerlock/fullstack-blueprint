"""`@task_execution` 装饰器单元测试（mock repository / session）。"""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from backend.infrastructure.async_task.execution import repository
from backend.infrastructure.async_task.execution.schemas import TaskExecutionStatus
from backend.infrastructure.async_task.taskiq.execution import task_execution


class _FakeSessionContext:
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, *args):
        return False


@pytest.fixture
def fake_factory(monkeypatch):
    session = AsyncMock()
    execution = SimpleNamespace(id=101)
    monkeypatch.setattr(repository, "next_attempt", AsyncMock(return_value=1))
    monkeypatch.setattr(repository, "create_running", AsyncMock(return_value=execution))
    monkeypatch.setattr(repository, "finish", AsyncMock())
    return (lambda: _FakeSessionContext(session)), execution


async def test_missing_outbox_id_rejected():
    @task_execution
    async def task(*, payload: dict):
        return None

    with pytest.raises(ValueError, match="outbox_id"):
        await task(payload={})


async def test_success_records_completed(fake_factory):
    factory, _execution = fake_factory

    @task_execution(session_factory=factory)
    async def task(*, payload: dict):
        assert payload == {"a": 1}
        return {"done": True}

    result = await task(payload={"a": 1}, outbox_id=7)
    assert result == {"done": True}

    repository.create_running.assert_awaited_once()
    repository.finish.assert_awaited_once()
    _, kwargs = repository.finish.call_args
    assert kwargs["status"] is TaskExecutionStatus.COMPLETED
    assert kwargs["result"] == {"done": True}


async def test_exception_records_failed_and_reraises(fake_factory):
    factory, _execution = fake_factory

    @task_execution(session_factory=factory)
    async def task(*, payload: dict):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await task(payload={}, outbox_id=7)

    _, kwargs = repository.finish.call_args
    assert kwargs["status"] is TaskExecutionStatus.FAILED
    assert kwargs["result"]["error_type"] == "RuntimeError"
    assert kwargs["result"]["error_message"] == "boom"


async def test_attempt_comes_from_repository(fake_factory, monkeypatch):
    factory, _execution = fake_factory
    monkeypatch.setattr(repository, "next_attempt", AsyncMock(return_value=3))

    @task_execution(session_factory=factory)
    async def task(*, payload: dict):
        return None

    await task(payload={}, outbox_id=7)
    repository.next_attempt.assert_awaited_once()
    repository.create_running.assert_awaited_once()
    args, _ = repository.create_running.call_args
    assert args[2] == 3
