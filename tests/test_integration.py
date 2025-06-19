import pytest
import numpy as np
from unittest.mock import MagicMock, AsyncMock

from karta.routing.router import KnowledgeRouter
from karta.manager import KartaManager
from karta.types import Fact

# Helper to create async generator
async def async_gen(data):
    for item in data:
        yield item

# Helper to collect items from an async generator for mocking
async def acollect(agen):
    return [item async for item in agen]

@pytest.mark.asyncio
async def test_router_uses_core_services(mock_plugin_manager_fixture):
    """Tests that the router uses the injected embedder and vector store."""
    # ARRANGE
    
    mock_embedder = AsyncMock()
    mock_vector_store = AsyncMock()
    mock_vector_store.add = AsyncMock()

    class MockRetrievedChunk:
        def __init__(self, id, score):
            self.id = id
            self.score = score
    mock_vector_store.search = AsyncMock(return_value=[MockRetrievedChunk("wikipedia_fact_dispatcher_v1", 0.9)])

    async def embed_side_effect(chunks, **kwargs):
        chunk_list = await acollect(chunks)
        if "some query" in chunk_list[0].content:
             return async_gen([("some query", np.array([1.0, 1.0, 1.0]))])
        else:
            return async_gen([
                (chunk_list[0], np.array([0.1, 0.2, 0.3])),
                (chunk_list[1], np.array([0.4, 0.5, 0.6])),
                (chunk_list[2], np.array([0.7, 0.8, 0.9])),
            ])
    mock_embedder.embed.side_effect = embed_side_effect

    router = KnowledgeRouter(mock_plugin_manager_fixture, mock_embedder, mock_vector_store, {})

    # ACT
    await router.setup()
    cascade = await router.get_provider_cascade("some query")

    # ASSERT
    assert mock_embedder.embed.call_count == 2
    mock_vector_store.add.assert_called_once()
    mock_vector_store.search.assert_called_once()
    assert "wikipedia_fact_dispatcher_v1" in cascade

@pytest.mark.asyncio
async def test_manager_executes_cascade(mock_plugin_manager_fixture):
    """Tests the manager's cascade logic, ensuring it tries providers until success."""
    # ARRANGE: Configure providers in the mock manager.
    wolfram_provider = mock_plugin_manager_fixture._plugins['wolfram_alpha_dispatcher_v1']
    wolfram_provider.lookup_fact = AsyncMock(return_value=None)

    wiki_provider = mock_plugin_manager_fixture._plugins['wikipedia_fact_dispatcher_v1']
    wiki_provider.lookup_fact = AsyncMock(return_value=Fact(entity="test", attribute="test", value="success", source="wiki"))

    # Mock the core services Karta Manager depends on
    mock_embedder = MagicMock()
    mock_vector_store = MagicMock()

    mock_plugin_manager_fixture.get_plugin_instance = AsyncMock(
        side_effect=lambda plugin_id, **kwargs: mock_plugin_manager_fixture._plugins.get(plugin_id)
    )

    manager = KartaManager(genie=MagicMock(), plugin_manager=mock_plugin_manager_fixture, embedder=mock_embedder, vector_store=mock_vector_store, config={})
    manager.router.get_provider_cascade = AsyncMock(return_value=['wolfram_alpha_dispatcher_v1', 'wikipedia_fact_dispatcher_v1'])

    # ACT
    result = await manager.lookup_fact("test", "test")

    # ASSERT
    wolfram_provider.lookup_fact.assert_called_once()
    wiki_provider.lookup_fact.assert_called_once()
    assert result and result.value == "success"