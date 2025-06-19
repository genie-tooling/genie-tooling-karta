import logging
from typing import List, Optional

from karta_for_genie.manager import KartaManager
from karta_for_genie.types import Entity, Fact

logger = logging.getLogger(__name__)

class KartaInterface:
    """The public, developer-facing interface for the Karta Engine."""
    def __init__(self, manager: KartaManager):
        self._manager = manager
        logger.info("KartaInterface created and attached to KartaManager.")

    async def recognize_entities(self, text: str, dispatcher_id: Optional[str] = None) -> List[Entity]:
        """Extracts named entities from a block of text."""
        return await self._manager.recognize_entities(text, dispatcher_id=dispatcher_id)

    async def summarize(self, text: str, style: str = "concise", dispatcher_id: Optional[str] = None) -> str:
        """Generates a summary of a text."""
        return await self._manager.summarize(text, style=style, dispatcher_id=dispatcher_id)

    async def lookup_fact(self, entity: str, attribute: str, dispatcher_id: Optional[str] = None) -> Optional[Fact]:
        """Looks up a single attribute or fact about a given entity."""
        return await self._manager.lookup_fact(entity, attribute, dispatcher_id=dispatcher_id)
