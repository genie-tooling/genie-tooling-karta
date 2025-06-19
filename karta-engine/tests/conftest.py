import pytest
from unittest.mock import MagicMock, AsyncMock
from typing import List, Type, Any, Dict, Optional

from karta_for_genie.dispatchers.abc import KnowledgeProvider, FactLookupDispatcher
from genie_tooling.core.types import Plugin

class MockPluginManager:
    """A mock PluginManager that aligns better with the real implementation."""
    def __init__(self, plugins: dict):
        self._plugins = plugins

    async def get_plugin_instance(self, plugin_id: str, **kwargs) -> Any:
        # Simulate getting an already instantiated plugin
        return self._plugins.get(plugin_id)

    async def get_all_plugin_instances_by_type(self, plugin_protocol_type: Type[Plugin]) -> List[Plugin]:
        # Simulate the real behavior of returning instances that match a protocol.
        return [
            instance for instance in self._plugins.values()
            if isinstance(instance, plugin_protocol_type)
        ]

@pytest.fixture
def mock_plugin_manager_fixture():
    # This fixture provides a plugin manager with a set of mock plugins
    # for testing discovery and routing.

    class MockWiki(FactLookupDispatcher, KnowledgeProvider):
        plugin_id = "wikipedia_fact_dispatcher_v1"
        knowledge_description = "Provides encyclopedic information."
        async def lookup_fact(self, *args, **kwargs): return MagicMock()
        # FIX: The setup method must accept the config dictionary.
        async def setup(self, config: Optional[Dict[str, Any]] = None, **kwargs): pass
        async def teardown(self): pass

    class MockWolfram(FactLookupDispatcher, KnowledgeProvider):
        plugin_id = "wolfram_alpha_dispatcher_v1"
        knowledge_description = "Provides mathematical and computational answers."
        async def lookup_fact(self, *args, **kwargs): return MagicMock()
        # FIX: The setup method must accept the config dictionary.
        async def setup(self, config: Optional[Dict[str, Any]] = None, **kwargs): pass
        async def teardown(self): pass

    class MockGoogle(KnowledgeProvider):
        plugin_id = "google_search_tool_v1"
        knowledge_description = "A general-purpose web search engine for recent events."
        async def execute(self, *args, **kwargs): return MagicMock()
        # FIX: The setup method must accept the config dictionary.
        async def setup(self, config: Optional[Dict[str, Any]] = None, **kwargs): pass
        async def teardown(self): pass


    plugins = {
        "wikipedia_fact_dispatcher_v1": MockWiki(),
        "wolfram_alpha_dispatcher_v1": MockWolfram(),
        "google_search_tool_v1": MockGoogle(),
        # FIX: Use AsyncMock here so that its methods are awaitable by default.
        "unrelated_tool_v1": AsyncMock()
    }
    return MockPluginManager(plugins)