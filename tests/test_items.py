import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_item(client: AsyncClient):
    response = await client.post(
        "/api/v1/items/",
        json={"title": "Test Item", "description": "This is a test item"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["title"] == "Test Item"
    assert data["description"] == "This is a test item"
    assert "id" in data


@pytest.mark.asyncio
async def test_read_items(client: AsyncClient):
    # First create an item
    await client.post(
        "/api/v1/items/",
        json={"title": "Test Item 1", "description": "Desc 1"},
    )
    await client.post(
        "/api/v1/items/",
        json={"title": "Test Item 2", "description": "Desc 2"},
    )

    response = await client.get("/api/v1/items/")
    assert response.status_code == 200
    result = response.json()
    assert result["data"]["total"] == 2
    items = result["data"]["items"]
    assert len(items) == 2
    assert items[0]["title"] == "Test Item 1"
    assert items[1]["title"] == "Test Item 2"
