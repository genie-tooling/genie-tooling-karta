# tests/scaffolds/genie_tooling/genie.py
# Functional Scaffold
import logging
from typing import TYPE_CHECKING, Any, Optional

from .config.models import MiddlewareConfig
from .config.resolver import ConfigResolver
from .core.plugin_manager import PluginManager
from .embedding_generators.abc import EmbeddingGeneratorPlugin
from .security.key_provider import KeyProvider
from .vector_stores.abc import VectorStorePlugin

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class Genie:
    """A functional scaffold of the Genie facade for testing."""

    _default_embedder: Optional[EmbeddingGeneratorPlugin] = None
    _default_vector_store: Optional[VectorStorePlugin] = None

    def __init__(self, plugin_manager: PluginManager, config: MiddlewareConfig):
        self._plugin_manager = plugin_manager
        self._config = config
        self.karta: Any = None
        logger.info("Genie Facade scaffold instantiated.")

    @classmethod
    async def create(
        cls,
        config: MiddlewareConfig,
        plugin_manager: Optional[PluginManager] = None,
        key_provider_instance: Optional[KeyProvider] = None,
    ) -> "Genie":
        """
        Creates a Genie instance. For testing, a pre-configured plugin_manager is required.
        """
        logger.info("Genie.create() called.")
        if not plugin_manager:
            raise ValueError("Functional scaffold requires a mock PluginManager.")

        # Resolve config to get default plugin IDs
        resolver = ConfigResolver()
        resolved_config = resolver.resolve(config, key_provider_instance)

        # FIX: Instantiate the default embedder and vector store based on the resolved config
        # This makes the scaffold behave more like the real Genie framework.
        embedder_id = resolved_config.default_rag_embedder_id
        vs_id = resolved_config.default_rag_vector_store_id

        default_embedder = None
        if embedder_id:
            embedder_config = resolved_config.embedding_generator_configurations.get(
                embedder_id, {}
            )
            embedder_any = await plugin_manager.get_plugin_instance(
                embedder_id, config=embedder_config
            )
            if isinstance(embedder_any, EmbeddingGeneratorPlugin):
                default_embedder = embedder_any

        default_vs = None
        if vs_id:
            vs_config = resolved_config.vector_store_configurations.get(vs_id, {})
            vs_any = await plugin_manager.get_plugin_instance(vs_id, config=vs_config)
            if isinstance(vs_any, VectorStorePlugin):
                default_vs = vs_any

        # Create the Genie instance
        genie_instance = cls(plugin_manager=plugin_manager, config=resolved_config)
        genie_instance._default_embedder = default_embedder
        genie_instance._default_vector_store = default_vs

        # --- FUNCTIONAL HANDSHAKE for Bootstrap Plugins ---
        karta_bootstrap_plugin = await plugin_manager.get_plugin(
            "karta_engine_bootstrap_v1"
        )
        if karta_bootstrap_plugin:
            logger.info("Karta bootstrap plugin found. Executing bootstrap...")
            await karta_bootstrap_plugin.bootstrap(genie=genie_instance)
        else:
            logger.warning("Karta bootstrap plugin not found in manager.")

        logger.info("Genie.create() finished.")
        return genie_instance

    async def get_default_embedder(self) -> Optional[EmbeddingGeneratorPlugin]:
        """Returns the default embedding generator instance."""
        return self._default_embedder

    async def get_default_vector_store(self) -> Optional[VectorStorePlugin]:
        """Returns the default vector store instance."""
        return self._default_vector_store

    async def close(self):
        logger.info("Genie facade closing down.")