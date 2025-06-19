# karta-engine/tests/conftest.py
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from unittest.mock import AsyncMock, MagicMock

import pytest

# FIX: Add the new 'scaffolds' directory to the Python path for the test session.
# This allows tests to `import genie_tooling` and get our dummy implementation.
scaffold_dir = Path(__file__).parent / "scaffolds"
sys.path.insert(0, str(scaffold_dir))

# Now that the path is set, we can import from the scaffolded modules.
from genie_tooling.core.types import Plugin
from karta_for_genie.dispatchers.abc import FactLookupDispatcher, KnowledgeProvider


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

    # FIX: Add a method to get a specific plugin for the bootstrap test.
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

    # Import the real bootstrap plugin to add it to the mock manager
    from karta_for_genie.bootstrap import KartaEngineBootstrapPlugin

    plugins = {
        "karta_engine_bootstrap_v1": KartaEngineBootstrapPlugin(),
        "wikipedia_fact_dispatcher_v1": MockWiki(),
        "wolfram_alpha_dispatcher_v1": MockWolfram(),
        "google_search_tool_v1": MockGoogle(),
        "unrelated_tool_v1": AsyncMock(),
    }
    return MockPluginManager(plugins)