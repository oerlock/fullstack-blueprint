from fastapi.testclient import TestClient

from backend.config.settings import CorsSettings
from backend.main import create_app


def client_with(cors_settings: CorsSettings | None = None) -> TestClient:
    app = create_app(cors_settings=cors_settings)
    return TestClient(app, raise_server_exceptions=False)


def test_ping():
    with client_with() as client:
        response = client.get("/ping")

    assert response.status_code == 200
    assert response.json() == {"message": "pong"}


def test_ready_reports_cache_dependency():
    with client_with() as client:
        response = client.get("/ready")

    body = response.json()
    assert body["dependencies"]["cache"] in {"ok", "unavailable"}
    if body["dependencies"]["cache"] == "ok":
        assert response.status_code == 200
        assert body["status"] == "ok"
    else:
        assert response.status_code == 503
        assert body["status"] == "unavailable"


def test_unknown_route_uses_unified_error_format():
    with client_with() as client:
        response = client.get("/api/v1/no-such-route")

    assert response.status_code == 404
    body = response.json()
    assert body["code"] == 404000
    assert body["message"] == "Not Found"
    assert body["metadata"] is None


def test_cors_middleware_applied_when_enabled():
    cors = CorsSettings(enabled=True, allow_origins=["https://example.com"])
    with client_with(cors) as client:
        response = client.get(
            "/ping",
            headers={"Origin": "https://example.com"},
        )

    assert response.headers["access-control-allow-origin"] == "https://example.com"


def test_cors_preflight():
    cors = CorsSettings(
        enabled=True,
        allow_origins=["https://example.com"],
        allow_methods=["GET", "POST"],
    )
    with client_with(cors) as client:
        response = client.options(
            "/ping",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://example.com"
