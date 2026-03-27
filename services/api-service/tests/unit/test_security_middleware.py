"""Test security middleware."""
import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from api_service.middleware.security_headers_middleware import SecurityHeadersMiddleware
from api_service.middleware.audit_middleware import AuditMiddleware


@pytest.fixture
def secure_app():
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    @app.get("/test")
    async def test_ep(): return {"ok": True}
    return app


@pytest.mark.asyncio
async def test_security_headers(secure_app):
    async with AsyncClient(transport=ASGITransport(app=secure_app), base_url="http://test") as c:
        r = await c.get("/test")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert "content-security-policy" in r.headers


@pytest.mark.asyncio
async def test_audit_does_not_block_get():
    app = FastAPI()
    app.add_middleware(AuditMiddleware)
    @app.get("/health")
    async def h(): return {"status": "ok"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/health")
    assert r.status_code == 200
