# karta-engine/showcase.py

import asyncio
import json
import logging
import os
from typing import Any

from genie_tooling.config.features import FeatureSettings
from genie_tooling.config.models import MiddlewareConfig
from genie_tooling.genie import Genie
from karta_for_genie.tools.entity_recognition_tool import entity_recognition_tool
from karta_for_genie.tools.fact_lookup_tool import fact_lookup_tool
from karta_for_genie.tools.summarization_tool import summarization_tool


def print_header(title: str):
    """Prints a formatted header to the console."""
    print("\n" + "=" * 60)
    print(f"🚀 {title.upper()}")
    print("=" * 60)


def print_result(description: str, result: Any):
    """Prints a formatted result to the console."""
    print(f"\n▶️  {description}")
    if isinstance(result, (dict, list)):
        print(json.dumps(result, indent=2, default=str))
    else:
        print(result)


async def run_karta_showcase():
    """
    A standalone script to demonstrate the capabilities of the Karta Engine
    integrated with Genie Tooling.
    """
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("genie_tooling").setLevel(logging.WARNING)
    logging.getLogger("karta_for_genie").setLevel(logging.INFO)


    # --- Check for API Keys ---
    wolfram_app_id = os.getenv("WOLFRAM_ALPHA_APP_ID")
    if not wolfram_app_id:
        print("\n" + "!" * 60)
        print("! ERROR: WOLFRAM_ALPHA_APP_ID environment variable not set.")
        print("! Please get a free App ID from the WolframAlpha Developer Portal")
        print("! and set it: export WOLFRAM_ALPHA_APP_ID='YOUR-APP-ID'")
        print("!" * 60)
        return

    # 1. --- Configuration ---
    # This configures Genie to use Ollama/Mistral and enables Karta's
    # plugins and tools.
    app_config = MiddlewareConfig(
        features=FeatureSettings(
            llm="ollama",
            llm_ollama_model_name="mistral",
            command_processor="llm_assisted",
            # Enable core RAG components, as Karta's router uses them
            rag_embedder="sentence_transformer",
            rag_vector_store="faiss",
        ),
        # Configure the Karta extension, providing the WolframAlpha App ID
        extension_configurations={
            "karta": {
                "fact_lookup": {
                    "dispatcher_specific_configs": {
                        "wolfram_alpha_dispatcher_v1": {"app_id": wolfram_app_id}
                    }
                }
            }
        },
        # Explicitly enable all Karta-provided tools so the LLM can use them
        tool_configurations={
            "entity_recognition_tool": {},
            "summarization_tool": {},
            "fact_lookup_tool": {},
        },
    )

    genie = None
    try:
        # 2. --- Initialization ---
        print_header("Initializing Genie and Karta Engine")
        genie = await Genie.create(config=app_config)

        # Register the function-based tools so the CommandProcessor can find them.
        await genie.register_tool_functions([
            entity_recognition_tool,
            summarization_tool,
            fact_lookup_tool,
        ])

        print("✅ Initialization Complete. Genie is ready.")
        assert hasattr(genie, "karta"), "Karta engine was not attached successfully."

        # 3. --- Direct Interface Showcase (genie.karta.*) ---
        print_header("Part 1: Using the Direct Karta Interface")

        # Summarization
        text_to_summarize = (
            "The James Webb Space Telescope (JWST) is a space telescope designed primarily "
            "to conduct infrared astronomy. As the largest optical telescope in space, its "
            "greatly improved infrared resolution and sensitivity allow it to view objects "
            "too old, distant, or faint for the Hubble Space Telescope."
        )
        summary = await genie.karta.summarize(text=text_to_summarize, style="one sentence")
        print_result("Summarization Result (Style: one sentence):", summary)

        # Entity Recognition
        text_for_ner = "Dr. Aris Thorne from Athens, Greece, joined the Genie-Tooling project in 2025."
        entities = await genie.karta.recognize_entities(text=text_for_ner)
        entity_dicts = [e.model_dump() for e in entities]
        print_result("Entity Recognition Result:", entity_dicts)

        # Fact Lookup (Should route to Wikipedia)
        fact_wiki = await genie.karta.lookup_fact(entity="Eiffel Tower", attribute="height")
        print_result("Fact Lookup (Encyclopedic - Smart Router):", fact_wiki.model_dump() if fact_wiki else "Fact not found.")

        # Fact Lookup (Should route to WolframAlpha)
        fact_wolfram = await genie.karta.lookup_fact(entity="Lead", attribute="melting point")
        print_result("Fact Lookup (Computational - Smart Router):", fact_wolfram.model_dump() if fact_wolfram else "Fact not found.")

        # 4. --- Agentic Tool Showcase (genie.run_command) ---
        print_header("Part 2: Using Karta Tools via LLM Agent")

        # Command for summarization_tool
        cmd_summary = f"Please give me a three-bullet-point summary of the following text: '{text_to_summarize}'"
        result_summary_tool = await genie.run_command(cmd_summary)
        print_result(f"Agent Command: '{cmd_summary}'", result_summary_tool)

        # Command for entity_recognition_tool
        cmd_ner = f"Extract all named entities from this sentence: '{text_for_ner}'"
        result_ner_tool = await genie.run_command(cmd_ner)
        print_result(f"Agent Command: '{cmd_ner}'", result_ner_tool)

        # Command for fact_lookup_tool (should route to Wikipedia)
        cmd_fact_wiki = "What is the primary language spoken in Brazil?"
        result_fact_wiki_tool = await genie.run_command(cmd_fact_wiki)
        print_result(f"Agent Command: '{cmd_fact_wiki}'", result_fact_wiki_tool)

        # Command for fact_lookup_tool (should route to WolframAlpha)
        cmd_fact_wolfram = "look up the value for the 20th Fibonacci number"
        result_fact_wolfram_tool = await genie.run_command(cmd_fact_wolfram)
        print_result(f"Agent Command: '{cmd_fact_wolfram}'", result_fact_wolfram_tool)

    except Exception as e:
        logging.error("An error occurred during the showcase: %s", e, exc_info=True)
    finally:
        if genie:
            print_header("Tearing Down Genie and Karta Engine")
            await genie.close()
            print("✅ Teardown Complete.")


if __name__ == "__main__":
    asyncio.run(run_karta_showcase())