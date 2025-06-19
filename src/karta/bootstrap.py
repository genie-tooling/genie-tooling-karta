import logging
from typing import TYPE_CHECKING

from genie_tooling.bootstrap import BootstrapPlugin
from karta.interface import KartaInterface
from karta.manager import KartaManager

if TYPE_CHECKING:
    from genie_tooling.genie import Genie

logger = logging.getLogger(__name__)

class KartaEngineBootstrapPlugin(BootstrapPlugin):
    """Initializes the Karta subsystem and attaches it to the Genie facade."""
    plugin_id: str = "karta_engine_bootstrap_v1"
    description: str = "Initializes and attaches the Karta Engine to the Genie facade."

    async def bootstrap(self, genie: "Genie") -> None:
        logger.info("KartaEngineBootstrapPlugin: Executing bootstrap logic...")

        # FIX: The config object is a private attribute of the Genie instance.
        karta_config = genie._config.extension_configurations.get("karta", {})

        # Use the new public accessors for shared components.
        core_embedder = await genie.get_default_embedder()
        core_vector_store = await genie.get_default_vector_store()

        if not core_embedder:
            raise RuntimeError("Karta Engine requires a default embedder to be configured in Genie.")
        if not core_vector_store:
            raise RuntimeError("Karta Engine requires a default vector store to be configured in Genie.")

        # The bootstrap plugin now correctly gets the main PluginManager from Genie.
        plugin_manager = genie._plugin_manager
        if not plugin_manager:
            raise RuntimeError("Karta Engine could not access the core PluginManager from the Genie instance.")

        karta_manager = KartaManager(
            genie=genie,
            plugin_manager=plugin_manager,
            embedder=core_embedder,
            vector_store=core_vector_store,
            config=karta_config
        )
        await karta_manager.setup()

        karta_interface = KartaInterface(manager=karta_manager)
        setattr(genie, "karta", karta_interface)

        logger.info("Intelligent `genie.karta` interface attached, using core embedding and vector store services.")