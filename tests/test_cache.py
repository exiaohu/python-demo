import pytest
from httpx import AsyncClient
from unittest.mock import MagicMock, patch
from app.core.config import settings

@pytest.mark.asyncio
async def test_cached_endpoint(client: AsyncClient):
    """
    Test that the caching decorator is working.
    Since we are using RedisBackend, we need Redis available or mocked.
    For this unit test, we can check if repeated calls return the same result.
    But verification of 'cache hit' vs 'miss' is harder without inspecting Redis.
    However, if the decorator is applied, it shouldn't crash.
    """
    
    # First call
    response1 = await client.get(f"{settings.API_V1_STR}/items/")
    assert response1.status_code == 200
    
    # Second call
    response2 = await client.get(f"{settings.API_V1_STR}/items/")
    assert response2.status_code == 200
    assert response1.json() == response2.json()

    # If we had a real Redis in CI, we could check keys.
    # For now, this ensures the integration doesn't break the app.
