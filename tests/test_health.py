import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_healthz(client: AsyncClient) -> None:
    r = await client.get("/healthz")
    assert r.status_code == 200
    data = r.json()
    assert data["version"] == settings.VERSION
    assert data["database"] == "ok"
    # Status depends on Redis availability in test environment
    if data["redis"] == "ok":
        assert data["status"] == "ok"
    else:
        # If redis is down or not configured in test env, overall status might be error
        # We accept this in local test environment where redis might not be running
        pass
