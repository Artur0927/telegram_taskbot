import pytest
from unittest.mock import AsyncMock, patch
from src import ai_engine, job_engine

@pytest.mark.asyncio
async def test_job_search_no_key():
    # Test that job search fails gracefully without key
    with patch.dict('os.environ', {}, clear=True):
        result = await job_engine.search_jobs("python")
        assert "RAPIDAPI_KEY is missing" in result

@pytest.mark.asyncio
async def test_ai_response_no_key():
    # Test that AI fails gracefully without key
    with patch.dict('os.environ', {}, clear=True):
        result = await ai_engine.generate_response("hello")
        assert "Missing RAPIDAPI_KEY" in result
