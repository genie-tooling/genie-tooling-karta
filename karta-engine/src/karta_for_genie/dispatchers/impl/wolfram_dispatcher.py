# karta-engine/src/karta_for_genie/dispatchers/impl/wolfram_dispatcher.py

import logging
import xml.etree.ElementTree as ET
from typing import Any, Dict, Optional

import httpx
from karta_for_genie.dispatchers.abc import FactLookupDispatcher, KnowledgeProvider
from karta_for_genie.types import Fact

logger = logging.getLogger(__name__)

try:
    import wolframalpha
except ImportError:
    wolframalpha = None


class WolframAlphaDispatcher(FactLookupDispatcher, KnowledgeProvider):
    """Answers computational and scientific queries using the WolframAlpha API."""

    plugin_id: str = "wolfram_alpha_dispatcher_v1"
    _client: Optional[Any] = None
    _http_client: httpx.AsyncClient

    @property
    def knowledge_description(self) -> str:
        return "Provides expert-level answers for mathematical computations, unit conversions, scientific formulas, algorithmically derived data, and quantitative facts. Best for queries that require calculation or precise scientific data."

    async def setup(self, config: Optional[Dict[str, Any]] = None):
        if wolframalpha is None:
            raise ImportError(
                "The 'wolframalpha' package is required. Install with `poetry add 'genie-tooling-karta[computation]'`."
            )

        config = config or {}
        app_id = config.get("app_id")
        self._http_client = httpx.AsyncClient(timeout=15.0)

        if app_id:
            try:
                # We still create the client object to get access to its app_id.
                self._client = wolframalpha.Client(app_id)
                logger.info(f"[{self.plugin_id}] WolframAlpha client initialized.")
            except Exception as e:
                logger.error(
                    f"Failed to initialize WolframAlpha client with provided app_id: {e}"
                )
                self._client = None
        else:
            logger.debug(
                f"[{self.plugin_id}] Deferring WolframAlpha client initialization until an app_id is provided."
            )

    async def lookup_fact(
        self,
        entity: str,
        attribute: str,
        genie: Any,
        config: Optional[Dict[str, Any]] = None,
    ) -> Optional[Fact]:
        if not self._client:
            await self.setup(config)

        if not self._client:
            logger.error(
                f"[{self.plugin_id}] Cannot lookup_fact because WolframAlpha client is not configured with a valid app_id."
            )
            return None

        query = f"{attribute} of {entity}"
        try:
            api_url = "https://api.wolframalpha.com/v2/query"
            # Define parameters for the API call.
            params = {
                "input": query,
                "appid": self._client.app_id,
                "format": "plaintext",  # Request plaintext for easier parsing
            }

            response = await self._http_client.get(api_url, params=params)
            response.raise_for_status()
            xml_content = response.content

            # FIX: Manually parse the XML using ElementTree.
            xml_root = ET.fromstring(xml_content)

            # Check if the query was successful at the API level.
            if xml_root.attrib.get("success") != "true":
                logger.warning(
                    f"WolframAlpha query for '{query}' was not successful. Response: {xml_content.decode()[:500]}"
                )
                return None

            # Find the primary result, which is typically in the pod with title="Result".
            # If not found, fall back to the first pod with plaintext.
            answer = None
            result_pod = xml_root.find('.//pod[@title="Result"]')
            if result_pod is not None:
                plaintext_element = result_pod.find(".//plaintext")
                if plaintext_element is not None and plaintext_element.text:
                    answer = plaintext_element.text.strip()

            # Fallback if the "Result" pod isn't present
            if answer is None:
                first_plaintext = xml_root.find(".//pod/subpod/plaintext")
                if first_plaintext is not None and first_plaintext.text:
                    answer = first_plaintext.text.strip()

            if answer:
                return Fact(
                    entity=entity, attribute=attribute, value=answer, source="WolframAlpha"
                )
            else:
                logger.debug(f"WolframAlpha query '{query}' returned no parsable result in pods.")
                return None

        except httpx.HTTPStatusError as e:
            logger.warning(
                f"WolframAlpha query failed for '{query}' with HTTP status {e.response.status_code}: {e.response.text}",
                exc_info=True,
            )
            return None
        except ET.ParseError as e_xml:
            logger.warning(
                f"WolframAlpha returned non-XML response for '{query}': {e_xml}",
                exc_info=True,
            )
            return None
        except Exception as e:
            logger.warning(
                f"WolframAlpha query failed for '{query}': {e}", exc_info=True
            )
            return None

    async def teardown(self) -> None:
        """Close the httpx client during teardown."""
        if hasattr(self, "_http_client") and self._http_client:
            await self._http_client.aclose()