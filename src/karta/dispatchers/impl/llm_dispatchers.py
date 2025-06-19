# karta-engine/src/karta/dispatchers/impl/llm_dispatchers.py

from typing import Dict, Any, Optional

from karta.dispatchers.abc import SummarizationDispatcher

class LlmSummaryDispatcher(SummarizationDispatcher):
    plugin_id: str = "llm_summary_dispatcher_v1"
    # FIX: Signature now matches protocol
    async def summarize(self, text: str, style: str, genie: Any, config: Optional[Dict[str, Any]] = None) -> str:
        config = config or {}
        llm_provider_id = config.get("llm_provider_id")
        prompt = f"Summarize the following text in a {style} manner:\n\n---\n{text}\n---"
        response = await genie.llm.generate(prompt=prompt, provider_id=llm_provider_id)
        return response.get("text", "")