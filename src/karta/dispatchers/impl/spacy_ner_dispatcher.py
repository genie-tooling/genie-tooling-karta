import logging
from typing import List, Dict, Any, Optional

from karta.dispatchers.abc import EntityRecognitionDispatcher
from karta.types import Entity

logger = logging.getLogger(__name__)

try:
    import spacy
    from spacy.language import Language
except ImportError:
    spacy = None
    Language = None

class SpacyNerDispatcher(EntityRecognitionDispatcher):
    """Performs named entity recognition using the spaCy library."""
    plugin_id: str = "spacy_ner_dispatcher_v1"
    _nlp: Optional[Language] = None

    async def setup(self, config: Optional[Dict[str, Any]] = None):
        if spacy is None:
            raise ImportError("The 'spacy' package is required. Please install it (`pip install spacy`).")
        
        config = config or {}
        model_name = config.get("spacy_model", "en_core_web_sm")
        
        try:
            self._nlp = spacy.load(model_name)
            logger.info(f"[{self.plugin_id}] Successfully loaded spaCy model '{model_name}'.")
        except OSError:
            logger.error(f"Could not find spaCy model '{model_name}'. Please download it via "
                         f"'python -m spacy download {model_name}'.")
            raise

    async def recognize_entities(self, text: str, config: Optional[Dict[str, Any]] = None) -> List[Entity]:
        if not self._nlp:
            await self.setup(config) # Lazy loading
        
        doc = self._nlp(text)
        entities = [
            Entity(text=ent.text, label=ent.label_, start_char=ent.start_char, end_char=ent.end_char)
            for ent in doc.ents
        ]
        return entities
