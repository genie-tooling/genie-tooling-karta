from typing import Dict, Any
from genie_tooling import tool


@tool
async def fact_lookup_tool(entity: str, attribute: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Looks up a specific attribute or fact about an entity using a smart-routing knowledge engine.
    This tool is capable of answering two main types of questions:
    1. Encyclopedic/General Knowledge: For facts about well-known public entities, concepts, and places (e.g., "height of Eiffel Tower", "capital of Japan", "primary language of Brazil").
    2. Computational/Scientific: For precise quantitative data, mathematical calculations, and scientific facts (e.g., "melting point of Lead", "20th Fibonacci number", "mass of the sun").
    Do NOT use this for summarization or general text understanding. Use it for targeted fact retrieval.

    Args:
        entity (str): The subject of the fact (e.g., 'Brazil', 'Fibonacci sequence').
        attribute (str): The property of the entity to find (e.g., 'primary language', '20th number').
        context (Dict[str, Any], optional): Invocation context from the framework.
    """
    genie_instance = context.get("genie_framework_instance")
    if not genie_instance or not hasattr(genie_instance, "karta"):
        return {"error": "The Karta Engine subsystem is not installed or available."}
    fact = await genie_instance.karta.lookup_fact(entity=entity, attribute=attribute)
    if not fact:
        return {"status": "not_found", "message": f"Could not find the '{attribute}' for '{entity}'."}
    return {"status": "found", "fact": fact.model_dump()}