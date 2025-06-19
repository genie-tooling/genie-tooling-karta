import logging
from typing import List, Dict, Any, Optional

from karta.dispatchers.abc import EntityRecognitionDispatcher
from karta.types import Entity

logger = logging.getLogger(__name__)

class NoOpEntityDispatcher(EntityRecognitionDispatcher):
    """
    A 'No Operation' dispatcher for entity recognition.
    It fulfills the protocol contract but performs no real work.
    Its purpose is to allow for end-to-end testing of the Karta Manager
    and Interface without requiring heavy NLP dependencies.
    """
    plugin_id: str = "no_op_entity_dispatcher_v1"

    async def setup(self, **kwargs):
        logger.info(f"[{self.plugin_id}] No-op dispatcher initialized. No action taken.")

    async def recognize_entities(self, text: str, config: Optional[Dict[str, Any]] = None) -> List[Entity]:
        logger.info(f"[{self.plugin_id}] 'recognize_entities' called. Returning placeholder data.")
        # Return a valid but empty list, fulfilling the contract.
        return []
