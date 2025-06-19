# Functional Scaffold
import logging
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

logger = logging.getLogger(__name__)

class Genie:
    """A functional scaffold of the Genie facade for testing."""
    def __init__(self, plugin_manager: Any, config: Dict[str, Any]):
        self.plugin_manager = plugin_manager
        self.config = config
        self.rag = MagicMock()
        self.llm = MagicMock()
        self.karta: Any = None
        logger.info("Genie Facade scaffold instantiated.")

    @classmethod
    async def create(cls, config: Dict[str, Any], plugin_manager: Optional[Any] = None) -> "Genie":
        """
        Creates a Genie instance. For testing, a pre-configured plugin_manager is required.
        """
        logger.info("Genie.create() called.")
        if not plugin_manager:
            raise ValueError("Functional scaffold requires a mock PluginManager.")

        genie_instance = cls(plugin_manager=plugin_manager, config=config)
        
        # --- FUNCTIONAL HANDSHAKE ---
        karta_bootstrap = await plugin_manager.get_plugin("karta_engine_bootstrap_v1")
        if karta_bootstrap:
            logger.info("Karta bootstrap plugin found. Executing setup...")
            # Ensure mock RAG manager exists for bootstrap to succeed in tests
            if not hasattr(genie_instance.rag, '_manager'):
                genie_instance.rag._manager = MagicMock()
            genie_instance.rag._manager.embedder = MagicMock()
            genie_instance.rag._manager.vector_store = MagicMock()
            await karta_bootstrap.setup(genie=genie_instance, plugin_manager=plugin_manager, config=config)
        else:
            logger.warning("Karta bootstrap plugin not found in manager.")

        logger.info("Genie.create() finished.")
        return genie_instance

    async def close(self):
        logger.info("Genie facade closing down.")