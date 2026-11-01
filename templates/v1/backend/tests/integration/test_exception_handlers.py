from fastapi import APIRouter
from fastapi.testclient import TestClient
from pydantic import BaseModel

from backend.main import create_app


def make_client() -> TestClient:
    app = create_app()
    debug_router = APIRouter()

    class EchoIn(BaseModel):
        value: int

    @debug_router.get("/boom")
    async def boom():
        raise RuntimeError("boom")

    @debug_router.post("/echo")
    async def echo(payload: EchoIn):
        return {"value": payload.value}

    app.include_router(debug_router)
    return TestClient(app, raise_server_exceptions=False)


def test_request_validation_error_uses_unified_format():
    with make_client() as client:
        response = client.post("/echo", json={"value": "not-an-int"})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == 422000
    assert body["message"] == "Request validation failed"
    errors = body["metadata"]["errors"]
    assert errors[0]["location"] == ["body", "value"]


def test_unhandled_exception_returns_500_without_details():
    with make_client() as client:
        response = client.get("/boom")

    assert response.status_code == 500
    body = response.json()
    assert body == {"code": 500001, "message": "Internal Server Error", "metadata": None}
