# Karta Engine: The Knowledge & Comprehension Subsystem

Karta Engine is an intelligent, pluggable knowledge and comprehension subsystem for the Genie Tooling ecosystem. Think of it as a specialized brain for your Genie agent, designed to understand unstructured text, look up facts, and provide insights on demand.

When integrated, Karta seamlessly attaches a powerful, high-level interface to your `genie` instance as `genie.karta`, providing direct access to its capabilities. It also registers a suite of agent-ready tools that your LLM can use automatically.

## Core Features

*   **Unified Interface (`genie.karta`)**: A clean, developer-friendly API for summarization, entity recognition, and fact lookups.
*   **Smart Fact-Finding**: The `lookup_fact` method uses a `KnowledgeRouter` to intelligently select the best backend for a query. It can route encyclopedic questions to Wikipedia and computational/scientific questions to WolframAlpha.
*   **Extensible Dispatchers**: The backend logic for each capability is handled by a "Dispatcher" plugin. This allows you to easily add new knowledge sources (e.g., a private database, another API) without changing your agent's code.
*   **Agent-Ready Tools**: Provides pre-built tools (`fact_lookup_tool`, `summarization_tool`, etc.) that are automatically discovered by Genie's `CommandProcessor`, allowing your agent to decide when to use Karta's abilities.

## How It Works: The Bootstrap Plugin

Karta Engine leverages the `genie-tooling` bootstrap mechanism for a zero-effort setup. When you install `genie-tooling-karta` alongside the core framework, its `KartaEngineBootstrapPlugin` automatically:
1.  Discovers all of Karta's internal components (dispatchers, tools).
2.  Initializes the `KartaManager` and its underlying `KnowledgeRouter`.
3.  Attaches the `KartaInterface` to your `genie` instance as `genie.karta`.

This means you get all of Karta's functionality without writing any complex initialization code.

## Installation

Install the core library along with the Karta Engine package. Use "extras" to enable the capabilities you need.

```bash
# For base functionality + NLP and all knowledge providers
pip install "genie-tooling-karta[full]"

# Or, install specific capabilities
pip install "genie-tooling-karta[nlp]"          # For SpaCy-based entity recognition
pip install "genie-tooling-karta[knowledge]"    # For Wikipedia
pip install "genie-tooling-karta[computation]"  # For WolframAlpha
```
**Post-install:**
1.  **SpaCy Model**: If you installed `[nlp]`, download a model: `python -m spacy download en_core_web_sm`
2.  **WolframAlpha API Key**: Get a free App ID from the WolframAlpha Developer Portal and set it as an environment variable:
    ```bash
    export WOLFRAM_ALPHA_APP_ID="YOUR-APP-ID"
    ```

## Configuration

Karta is designed to be nearly zero-config if dependencies are installed. You only need to configure it if you want to override defaults or provide API keys.

Configuration is done in your `MiddlewareConfig` object.

```python
# In your main application's config
import os

app_config = MiddlewareConfig(
    # 1. Enable core features Karta depends on for routing
    features=FeatureSettings(
        llm="ollama", # An LLM is needed for some dispatchers
        rag_embedder="sentence_transformer",
        rag_vector_store="faiss",
    ),

    # 2. Enable the Karta-provided tools for the agent
    tool_configurations={
        "entity_recognition_tool": {},
        "summarization_tool": {},
        "fact_lookup_tool": {},
    },

    # 3. (Optional) Provide specific configurations for Karta's extensions
    extension_configurations={
        "karta": {
            "fact_lookup": {
                # Example: Provide the WolframAlpha App ID
                "dispatcher_specific_configs": {
                    "wolfram_alpha_dispatcher_v1": {
                        "app_id": os.getenv("WOLFRAM_ALPHA_APP_ID")
                    }
                }
            }
        }
    },
)
```

## Usage Examples

Once `genie` is initialized with the config above, you can use Karta in two ways:

### 1. Direct Interface (`genie.karta.*`)

Use Karta's capabilities directly in your application code.

```python
import asyncio

async def use_karta_directly(genie):
    # Example 1: Summarization
    text = "The James Webb Space Telescope (JWST) is a space telescope..."
    summary = await genie.karta.summarize(text=text, style="one sentence")
    print(f"Summary: {summary}")

    # Example 2: Entity Recognition
    entities = await genie.karta.recognize_entities(text="Dr. Aris Thorne from Athens, Greece.")
    print(f"Entities: {[e.model_dump() for e in entities]}")

    # Example 3: Smart Fact Lookup (will route to WolframAlpha)
    fact = await genie.karta.lookup_fact(entity="Lead", attribute="melting point")
    print(f"Fact: {fact.model_dump() if fact else 'Not found'}")
```

### 2. Agentic Tools (`genie.run_command`)

Let the LLM agent decide when to use Karta's tools.

```python
import asyncio

async def use_karta_agentically(genie):
    # The LLM will choose 'fact_lookup_tool' and determine the parameters
    result = await genie.run_command("What is the highest mountain in North America?")
    print(result)

    # The LLM will choose 'summarization_tool'
    result = await genie.run_command("Give me a three-bullet summary of this article: [long article text]")
    print(result)
```

## What's Inside?

Karta Engine is composed of several key components:
*   **`KnowledgeRouter`**: The core of smart fact-finding. It uses vector search on component descriptions to decide which dispatcher is best suited to answer a query.
*   **`Dispatchers`**: The backend implementations for each capability.
    *   `SpacyNerDispatcher`: For entity recognition.
    *   `LlmSummaryDispatcher`: For summarization using Genie's configured LLM.
    *   `WikipediaFactDispatcher`: For looking up encyclopedic facts.
    *   `WolframAlphaDispatcher`: For computational and scientific facts.
*   **`Tools`**: Agent-facing functions that use the `KartaInterface` to expose its capabilities to the LLM.