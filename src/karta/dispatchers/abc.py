# karta-engine/src/karta/dispatchers/abc.py

from typing import Protocol, List, Dict, Any, Optional, runtime_checkable

from karta.types import Entity, Fact
from genie_tooling.core.types import Plugin

@runtime_checkable
class KnowledgeProvider(Protocol):
    @property
    def knowledge_description(self) -> str: ...

@runtime_checkable
class FactLookupDispatcher(Plugin, Protocol):
    # FIX: Ensure 'genie' is part of the protocol signature
    async def lookup_fact(self, entity: str, attribute: str, genie: Any, config: Optional[Dict[str, Any]] = None) -> Optional[Fact]: ...

@runtime_checkable
class EntityRecognitionDispatcher(Plugin, Protocol):
    async def recognize_entities(self, text: str, config: Optional[Dict[str, Any]] = None) -> List[Entity]: ...

@runtime_checkable
class SummarizationDispatcher(Plugin, Protocol):
    # FIX: Ensure 'genie' is part of the protocol signature
    async def summarize(self, text: str, style: str, genie: Any, config: Optional[Dict[str, Any]] = None) -> str: ...