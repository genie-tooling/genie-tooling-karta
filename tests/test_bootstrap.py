# karta-engine/tests/test_bootstrap.py
import pytest

# Because of conftest.py, these imports now work and point to our dummy implementations.
from genie_tooling.config.models import MiddlewareConfig
from genie_tooling.genie import Genie
from karta.interface import KartaInterface


@pytest.mark.asyncio
async def test_bootstrap_attaches_karta_interface_correctly(
    mock_plugin_manager_fixture,
):
    """
    Tests that Karta's bootstrap plugin correctly attaches the KartaInterface
    to the Genie instance. This test now uses a mock plugin manager that
    includes the real bootstrap plugin, which is then run by the scaffolded
    Genie.create() method.
    """
    # ARRANGE
    # The config that the bootstrap plugin will read.
    app_config = MiddlewareConfig(
        features={
            # These features are still needed for ConfigResolver to run.
            "rag_embedder": "sentence_transformer",
            "rag_vector_store": "faiss",
        },
        # Add a dummy extension config section for the bootstrap to read
        extension_configurations={"karta": {}},
    )

    # ACT: Call the scaffolded Genie.create(). It will discover and run the
    # real KartaEngineBootstrapPlugin (provided by the fixture), which will
    # now receive the mocked services from the scaffolded Genie instance.
    genie_instance = await Genie.create(
        config=app_config, plugin_manager=mock_plugin_manager_fixture
    )

    # ASSERT
    # Now, this assertion should pass because the bootstrap no longer raises an error.
    assert hasattr(
        genie_instance, "karta"
    ), "Bootstrap failed to attach 'karta' attribute."
    assert isinstance(
        genie_instance.karta, KartaInterface
    ), "'karta' attribute is not a KartaInterface instance."