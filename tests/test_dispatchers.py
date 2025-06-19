# karta-engine/tests/test_dispatchers.py
import logging

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# --- Test Individual Dispatchers ---


@patch("karta_for_genie.dispatchers.impl.spacy_ner_dispatcher.spacy")
@pytest.mark.asyncio
async def test_spacy_dispatcher(mock_spacy):
    """Tests the SpacyNerDispatcher by mocking the spacy library."""
    from karta_for_genie.dispatchers.impl.spacy_ner_dispatcher import SpacyNerDispatcher

    mock_ent = MagicMock()
    mock_ent.text, mock_ent.label_, mock_ent.start_char, mock_ent.end_char = (
        "Aris Thorne",
        "PERSON",
        5,
        16,
    )
    mock_doc = MagicMock()
    mock_doc.ents = [mock_ent]
    mock_nlp = MagicMock(return_value=mock_doc)
    mock_spacy.load.return_value = mock_nlp
    dispatcher = SpacyNerDispatcher()
    entities = await dispatcher.recognize_entities(text="Hi, Aris Thorne here.")
    assert len(entities) == 1 and entities[0].label == "PERSON"


@patch("karta_for_genie.dispatchers.impl.wikipedia_dispatcher.wikipediaapi.Wikipedia")
@pytest.mark.asyncio
async def test_wikipedia_dispatcher_finds_fact(mock_wiki_class):
    """Tests Wikipedia dispatcher success path by mocking the library."""
    from karta_for_genie.dispatchers.impl.wikipedia_dispatcher import WikipediaFactDispatcher

    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.summary = "The height is 330 m."
    mock_page.fullurl = "https://en.wikipedia.org/wiki/Eiffel_Tower"
    mock_wiki_client = MagicMock()
    mock_wiki_client.page.return_value = mock_page
    mock_wiki_class.return_value = mock_wiki_client

    # Create a mock genie instance because the dispatcher now uses it for LLM extraction.
    mock_genie = MagicMock()
    mock_genie.llm = MagicMock()
    # Configure the mock LLM to return the expected value.
    mock_genie.llm.generate = AsyncMock(return_value={"text": "330 m"})

    dispatcher = WikipediaFactDispatcher()
    # Pass the mock genie instance to the lookup_fact method.
    fact = await dispatcher.lookup_fact("Eiffel Tower", "height", genie=mock_genie)

    assert fact is not None
    assert fact.value == "330 m"
    assert fact.source == "https://en.wikipedia.org/wiki/Eiffel_Tower"


@patch("karta_for_genie.dispatchers.impl.wolfram_dispatcher.httpx.AsyncClient")
@pytest.mark.asyncio
async def test_wolfram_dispatcher_correctly_mocked(mock_httpx_client_class):
    """Tests Wolfram dispatcher by mocking the httpx library client."""
    from karta_for_genie.dispatchers.impl.wolfram_dispatcher import WolframAlphaDispatcher
    from karta_for_genie.types import Fact

    # Mock the response from httpx.get()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.content = b"""<?xml version='1.0' encoding='UTF-8'?>
<queryresult success='true'>
    <pod title='Result' primary='true'>
        <subpod>
            <plaintext>42</plaintext>
        </subpod>
    </pod>
</queryresult>"""

    # Configure the async client mock that will be the return value of httpx.AsyncClient()
    mock_async_client = AsyncMock()
    mock_async_client.get = AsyncMock(return_value=mock_response)
    # FIX: Assign the mock instance directly to the return_value of the patched class.
    # This ensures that when the dispatcher's setup calls `httpx.AsyncClient()`, it gets our mock.
    mock_httpx_client_class.return_value = mock_async_client

    dispatcher = WolframAlphaDispatcher()
    with patch(
        "karta_for_genie.dispatchers.impl.wolfram_dispatcher.wolframalpha.Client"
    ) as mock_wolfram_client:
        mock_wolfram_client.return_value.app_id = "FAKE-ID"
        await dispatcher.setup(config={"app_id": "FAKE-ID"})

        # ACT
        fact = await dispatcher.lookup_fact("universe", "meaning", genie=None)

    # ASSERT
    assert fact is not None
    assert isinstance(fact, Fact)
    assert fact.value == "42"
    mock_async_client.get.assert_called_once()


# --- NEW TEST FOR NO-OP DISPATCHER ---
@pytest.mark.asyncio
async def test_no_op_dispatcher(caplog: pytest.LogCaptureFixture):
    """Tests the NoOpEntityDispatcher to ensure it returns an empty list."""
    from karta_for_genie.dispatchers.impl.no_op_dispatchers import NoOpEntityDispatcher

    caplog.set_level(logging.INFO)

    dispatcher = NoOpEntityDispatcher()

    # Test setup (should be a no-op but run without error)
    await dispatcher.setup()
    assert "No-op dispatcher initialized" in caplog.text
    caplog.clear()

    # Test main functionality
    entities = await dispatcher.recognize_entities(text="This text will be ignored.")

    # Assert that the result is an empty list, as per the contract.
    assert entities == []
    assert "'recognize_entities' called. Returning placeholder data." in caplog.text