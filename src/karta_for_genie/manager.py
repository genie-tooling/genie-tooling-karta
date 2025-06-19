import logging
from typing import Any, Dict, Optional

from genie_tooling.tools.manager import ToolManager
from karta.dispatchers.abc import (
    FactLookupDispatcher,
    SummarizationDispatcher,
)
from karta.routing.router import KnowledgeRouter
from karta.types import Fact

logger = logging.getLogger(__name__)

class KartaManager:
    """Orchestrates knowledge tasks by using the KnowledgeRouter."""
    def __init__(self, genie: Any, plugin_manager: Any, embedder: Any, vector_store: Any, config: Dict[str, Any]):
        self.genie = genie
        self.plugin_manager = plugin_manager
        
        self.config = config
        self.router = KnowledgeRouter(plugin_manager, embedder, vector_store, self.config.get("fact_lookup", {}))

    async def setup(self):
        await self.router.setup()

    async def lookup_fact(self, entity: str, attribute: str, dispatcher_id: Optional[str] = None):
        if dispatcher_id:
            cascade = [dispatcher_id]
        else:
            cascade = await self.router.get_provider_cascade(f"{entity} {attribute}")

        for provider_id in cascade:
            
            provider = await self.plugin_manager.get_plugin_instance(provider_id)
            if not provider:
                continue

            result = None
            if isinstance(provider, FactLookupDispatcher):
                result = await provider.lookup_fact(entity, attribute, self.genie)
            
            elif isinstance(provider, ToolManager):
                tool_result = await provider.execute(params={"query": f"{attribute} of {entity}"}, context={})
                if tool_result and not tool_result.get("error"):
                    answer = tool_result.get("answer") or tool_result.get("result")
                    if answer:
                        result = Fact(entity=entity, attribute=attribute, value=str(answer), source=provider.plugin_id)

            if result:
                return result
        return None

    async def summarize(self, text: str, style: str, dispatcher_id: Optional[str] = None):
        summary_config = self.config.get("summarization", {})
        target_id = dispatcher_id or summary_config.get("dispatcher_id", "llm_summary_dispatcher_v1")
        dispatcher = await self.plugin_manager.get_plugin_instance(target_id)
        if isinstance(dispatcher, SummarizationDispatcher):
            return await dispatcher.summarize(text, style, self.genie, summary_config.get("dispatcher_config"))
        return "Error: No valid summarization dispatcher found."

    async def recognize_entities(self, text: str, dispatcher_id: Optional[str] = None):
        entity_config = self.config.get("entity_recognition", {})
        target_id = dispatcher_id or entity_config.get("dispatcher_id", "spacy_ner_dispatcher_v1")
        dispatcher = await self.plugin_manager.get_plugin_instance(target_id)
        from karta.dispatchers.abc import EntityRecognitionDispatcher
        if isinstance(dispatcher, EntityRecognitionDispatcher):
            return await dispatcher.recognize_entities(text=text, config=entity_config.get("dispatcher_config"))
        return []