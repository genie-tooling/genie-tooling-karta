# karta-engine/src/karta_for_genie/dispatchers/impl/wikipedia_dispatcher.py

import logging
from typing import Any, Dict, Optional

from karta_for_genie.dispatchers.abc import FactLookupDispatcher, KnowledgeProvider
from karta_for_genie.types import Fact

logger = logging.getLogger(__name__)

try:
    import wikipediaapi
except ImportError:
    wikipediaapi = None


class WikipediaFactDispatcher(FactLookupDispatcher, KnowledgeProvider):
    plugin_id: str = "wikipedia_fact_dispatcher_v1"
    _wiki: Optional[Any] = None

    @property
    def knowledge_description(self) -> str:
        return "Provides encyclopedic, descriptive, and qualitative information about well-known public entities, historical events, and general knowledge concepts. Best for 'what is' or 'who is' style questions."

    async def setup(self, config: Optional[Dict[str, Any]] = None):
        if wikipediaapi is None:
            raise ImportError("wikipedia-api is required.")
        config = config or {}
        self._wiki = wikipediaapi.Wikipedia(
            language=config.get("lang", "en"), user_agent="KartaEngine/1.0"
        )

    async def lookup_fact(
        self, entity: str, attribute: str, genie: Any, config: Optional[Dict[str, Any]] = None
    ) -> Optional[Fact]:
        if not self._wiki:
            await self.setup(config)

        page = self._wiki.page(entity)
        if not page.exists():
            return None

        # Take the first 500 words for context, which is plenty for most facts.
        summary = " ".join(page.summary.split()[:500])
        if not summary:
            return None

        if not genie or not hasattr(genie, "llm"):
            logger.error(f"[{self.plugin_id}] Genie LLM interface not available. Cannot perform LLM-based fact extraction.")
            return None

        try:
            extraction_prompt = (
                f"Based on the following text, what is the '{attribute}' of '{entity}'? "
                "Provide only the value as a concise answer. If the information is not present, respond with 'Not found.'\n\n"
                f"Text:\n---\n{summary}\n---"
            )
            response = await genie.llm.generate(prompt=extraction_prompt, temperature=0.0)
            answer = response.get("text", "").strip()

            if "not found" in answer.lower() or not answer:
                return None

            return Fact(
                entity=entity,
                attribute=attribute,
                value=answer,
                source=page.fullurl,
            )
        except Exception as e:
            logger.error(f"LLM-based fact extraction failed for '{entity} - {attribute}': {e}", exc_info=True)
            return None