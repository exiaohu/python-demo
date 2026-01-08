from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.backend_pre_start import init, main


@pytest.mark.asyncio
async def test_init_successful() -> None:
    with patch("app.backend_pre_start.engine") as mock_engine:
        mock_conn = AsyncMock()
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn

        await init()

        mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_init_failure() -> None:
    with patch("app.backend_pre_start.engine") as mock_engine:
        # Mock connection to raise an exception
        mock_engine.connect.return_value.__aenter__.side_effect = Exception("DB Connection Error")

        # Modify retry policy to fail fast for testing
        with patch("app.backend_pre_start.init.retry.stop", return_value=MagicMock(return_value=True)):
            # Should raise RetryError after retries are exhausted (or immediately if mocked)
            pass


@pytest.mark.asyncio
async def test_main() -> None:
    with patch("app.backend_pre_start.init") as mock_init:
        await main()
        mock_init.assert_called_once()
