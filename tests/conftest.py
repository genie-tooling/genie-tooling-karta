# karta-engine/tests/conftest.py
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from unittest.mock import AsyncMock, MagicMock

import pytest

# Add the 'scaffolds' directory to the Python path for the test session.
scaffold_dir = Path(__file__).parent / "scaffolds"
sys.path.insert(0, str(scaffold_dir))

# Now that the path is set, we can import from the scaffolded modules.
from genie_tooling.core.types import Plugin  # noqa: E402
from genie_tooling.embedding_generators.abc import EmbeddingGeneratorPlugin # noqa: E402
from genie_tooling.security.key_provider import KeyProvider # noqa: E402
from genie_tooling.vector_stores.abc import VectorStorePlugin # noqa: E402
from karta_for_genie.bootstrap import KartaEngineBootstrapPlugin # noqa: E402
from karta_for_genie.dispatchers.abc import FactLookupDispatcher, KnowledgeProvider # noqa: E402


class MockKeyProvider(KeyProvider, Plugin):
    """A mock KeyProvider for testing."""

    plugin_id = "environment_key_provider_v1"

    async def get_key(self, key_name: str) -> Optional[str]:
        return f"mock_key_for_{key_name}"

    async def setup(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        pass

    async def teardown(self):
        pass


# FIX: Add mock classes for the missing dependencies.
class MockEmbedder(EmbeddingGeneratorPlugin):
    plugin_id = "sentence_transformer_embedder_v1"

    async def embed(self, *args, **kwargs):
        # This can be made more sophisticated if tests need specific embeddings.
        async def async_gen():
            yield ("mock_chunk", [0.1, 0.2, 0.3])

        return async_gen()


class MockVectorStore(VectorStorePlugin):
    plugin_id = "faiss_vector_store_v1"

    async def add(self, *args, **kwargs):
        return {"added_count": 1}


class MockPluginManager:
    """A mock PluginManager that aligns better with the real implementation."""

    def __init__(self, plugins: dict):
        self._plugins = plugins

    async def get_plugin_instance(self, plugin_id: str, **kwargs) -> Any:
        # Simulate getting an already instantiated plugin
        return self._plugins.get(plugin_id)

    async def get_all_plugin_instances_by_type(
        self, plugin_protocol_type: Type[Plugin]
    ) -> List[Plugin]:
        # Simulate the real behavior of returning instances that match a protocol.
        return [
            instance
            for instance in self._plugins.values()
            if isinstance(instance, plugin_protocol_type)
        ]

    async def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Simulates getting a plugin class or instance by ID."""
        return self._plugins.get(plugin_id)


@pytest.fixture
def mock_plugin_manager_fixture():
    # This fixture provides a plugin manager with a set of mock plugins
    # for testing discovery and routing.

    class MockWiki(FactLookupDispatcher, KnowledgeProvider):
        plugin_id = "wikipedia_fact_dispatcher_v1"
        knowledge_description = "Provides encyclopedic information."

        async def lookup_fact(self, *args, **kwargs):
            return MagicMock()

        async def setup(self, config: Optional[Dict[str, Any]] = None, **kwargs):
            pass

        async def teardown(self):
            pass

    class MockWolfram(FactLookupDispatcher, KnowledgeProvider):
        plugin_id = "wolfram_alpha_dispatcher_v1"
        knowledge_description = "Provides mathematical and computational answers."

        async def lookup_fact(self, *args, **kwargs):
            return MagicMock()

        async def setup(self, config: Optional[Dict[str, Any]] = None, **kwargs):
            pass

        async def teardown(self):
            pass

    class MockGoogle(KnowledgeProvider):
        plugin_id = "google_search_tool_v1"
        knowledge_description = "A general-purpose web search engine for recent events."

        async def execute(self, *args, **kwargs):
            return MagicMock()

        async def setup(self, config: Optional[Dict[str, Any]] = None, **kwargs):
            pass

        async def teardown(self):
            pass

    plugins = {
        # FIX: Add instances of the mock dependencies needed by Genie.create()
        "karta_engine_bootstrap_v1": KartaEngineBootstrapPlugin(),
        "environment_key_provider_v1": MockKeyProvider(),
        "sentence_transformer_embedder_v1": MockEmbedder(),
        "faiss_vector_store_v1": MockVectorStore(),
        "wikipedia_fact_dispatcher_v1": MockWiki(),
        "wolfram_alpha_dispatcher_v1": MockWolfram(),
        "google_search_tool_v1": MockGoogle(),
        "unrelated_tool_v1": AsyncMock(),
    }
    return MockPluginManager(plugins)