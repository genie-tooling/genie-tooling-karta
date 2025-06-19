import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from genie_tooling.config.models import MiddlewareConfig
from genie_tooling.genie import Genie
from karta_for_genie.bootstrap import KartaEngineBootstrapPlugin
from karta_for_genie.interface import KartaInterface

@pytest.mark.asyncio
async def test_bootstrap_attaches_karta_interface_correctly():
    """
    Tests that Karta's bootstrap plugin correctly attaches the KartaInterface
    to the Genie instance. This test now mocks the underlying services
    that were failing due to missing libraries in the test environment.
    """
    # ARRANGE
    # We still want to test the real bootstrap logic, but we must provide
    # mock dependencies that it expects from Genie.
    mock_embedder = AsyncMock()
    mock_vector_store = AsyncMock()

    # The config that the bootstrap plugin will read.
    app_config = MiddlewareConfig(
        features={
            # These features are still needed for ConfigResolver to run.
            "rag_embedder": "sentence_transformer",
            "rag_vector_store": "faiss",
        }
    )

    # Patch the `get_default_embedder` and `get_default_vector_store` methods
    # on the Genie facade itself. When the Karta bootstrap calls them,
    # they will return our mocks instead of failing.
    with patch.object(Genie, 'get_default_embedder', return_value=mock_embedder), \
         patch.object(Genie, 'get_default_vector_store', return_value=mock_vector_store):

        # ACT: Call the real Genie.create(). It will discover and run the
        # KartaEngineBootstrapPlugin, which will now receive the mocked services.
        genie_instance = await Genie.create(config=app_config)

        # ASSERT
        # Now, this assertion should pass because the bootstrap no longer raises a RuntimeError.
        assert hasattr(genie_instance, "karta"), "Bootstrap failed to attach 'karta' attribute."
        assert isinstance(genie_instance.karta, KartaInterface), "'karta' attribute is not a KartaInterface instance."