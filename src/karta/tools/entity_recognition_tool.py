# karta-engine/src/karta/tools/entity_recognition_tool.py
from typing import Any, Dict, List

from genie_tooling import tool


@tool
async def entity_recognition_tool(
    text: str, context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Extracts named entities (such as people, places, organizations, dates) from a given block of text.
    Use this tool when you need to identify *what* is mentioned in a text, not for looking up facts about those things.
    For example, if the command is "Who and where is mentioned in 'Dr. Aris Thorne from Athens'?", this tool is the correct choice.

    Args:
        text (str): The text to extract named entities from.
        context (Dict[str, Any]): The invocation context from the framework, which contains the Genie instance.
    """
    genie_instance = context.get("genie_framework_instance")

    if not genie_instance or not hasattr(genie_instance, "karta"):
        return {"error": "The Karta Engine subsystem is not installed or available."}

    # The type hint helps with static analysis, but the object is already a full Genie instance.
    from karta.types import Entity

    entities: List[Entity] = await genie_instance.karta.recognize_entities(text=text)
    return {"entities": [entity.model_dump() for entity in entities]}