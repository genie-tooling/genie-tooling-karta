# karta-engine/src/karta/tools/summarization_tool.py
from typing import Any, Dict

from genie_tooling import tool


@tool
async def summarization_tool(
    text: str,
    style: str = "a few concise bullet points",
    context: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Generates a summary of a long piece of text."""
    genie_instance = context.get("genie_framework_instance") if context else None

    if not genie_instance or not hasattr(genie_instance, "karta"):
        return {"error": "The Karta Engine subsystem is not installed or available."}

    summary = await genie_instance.karta.summarize(text=text, style=style)
    return {"summary": summary} if summary else {"error": "Failed to generate a summary."}