import pytest
import httpx

# Import only the real components we need to interact with.
from genie_tooling.genie import Genie
from genie_tooling.config.models import MiddlewareConfig

def is_ollama_running():
    """Checks if a local Ollama service is responsive."""
    try:
        httpx.get("http://localhost:11434", timeout=1)
        return True
    except httpx.ConnectError:
        return False

@pytest.mark.e2e
@pytest.mark.skipif(not is_ollama_running(), reason="Ollama service is not running")
@pytest.mark.asyncio
async def test_e2e_full_system_with_live_ollama():
    """
    Tests the Karta integration by letting the real Genie framework discover
    and initialize all correctly packaged plugins.
    """
    # ARRANGE
    # FIX: The E2E test must configure all features that the Karta bootstrap depends on.
    app_config = MiddlewareConfig(
        features={
            "llm": "ollama",
            "llm_ollama_model_name": "mistral",
            "rag_embedder": "sentence_transformer", # This was missing
            "rag_vector_store": "faiss",             # This was missing
        },
        # Correctly using the new extension configuration field
        extension_configurations={
            "karta": {
                "summarization": {"dispatcher_id": "llm_summary_dispatcher_v1"}
            }
        }
    )

    genie = None
    try:
        # ACT: Initialize Genie. Its `create` method will now correctly find
        # and execute the `KartaEngineBootstrapPlugin.bootstrap` method.
        # This will now work because the required dependencies (embedder, vs) are configured.
        genie = await Genie.create(config=app_config)

        # ASSERT 1: The bootstrap was successful.
        assert hasattr(genie, "karta") and genie.karta is not None, "Bootstrap failed."

        # ACT 2: Call the end-to-end functionality.
        text = "The sun is a star. It is very big. It is also very hot. Plasma."
        summary = await genie.karta.summarize(text=text, style="four words")

        # ASSERT 2: The E2E call worked as expected.
        assert summary is not None and isinstance(summary, str)
        assert len(summary.split()) < 8

    finally:
        if genie:
            await genie.close()