import pytest

from backend.errors.base import AppError
from backend.errors.codes import AENotFound, AEValidationError


def test_default_message_and_metadata():
    exc = AENotFound()

    assert exc.code == 404001
    assert exc.message == "资源不存在"
    assert exc.metadata is None


def test_custom_message_and_metadata():
    exc = AENotFound("线程不存在: 123", metadata={"thread_id": 123})

    assert exc.message == "线程不存在: 123"
    assert exc.metadata == {"thread_id": 123}


def test_status_code_derived_from_code():
    assert AENotFound().status_code == 404
    assert AEValidationError().status_code == 422


@pytest.mark.parametrize(
    ("exc_type", "code"),
    [
        (AENotFound, 404001),
        (AEValidationError, 422001),
    ],
)
def test_ae_exceptions_inherit_app_error(exc_type, code):
    assert issubclass(exc_type, AppError)
    assert exc_type.code == code


def test_exception_is_raisable_and_catchable():
    with pytest.raises(AppError, match="资源不存在"):
        raise AENotFound
