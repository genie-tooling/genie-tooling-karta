# Using the Karta Engine (Intelligent Edition)

The Karta Engine is a powerful, optional subsystem for `genie-tooling` that provides advanced, self-discovering natural language understanding capabilities.

## 1. Philosophy: "Kitchen-Sink Included"

Karta is designed to work out-of-the-box. If you have installed its dependencies, it will automatically discover and use all available knowledge providers (Wikipedia, WolframAlpha, spaCy, core Genie tools, etc.) without requiring any initial configuration. You only need to add a `karta_configurations` block if you want to *override* the intelligent defaults.

## 2. Installation

Install the core library along with the Karta Engine package. Use "extras" to enable the capabilities you need.

```bash
# For base functionality + Wikipedia & WolframAlpha
pip install "genie-tooling-karta[knowledge,computation]"

# For NLP and embedding-based routing
pip install "genie-tooling-karta[nlp,embedding]"

# To install everything
pip install "genie-tooling-karta[nlp,knowledge,computation,embedding]"
```

You will also need to download a `spaCy` model (`python -m spacy download en_core_web_sm`) and acquire an App ID for WolframAlpha.

## 3. Configuration (Optional)

You only need this block to customize behavior.

```python
# In your MiddlewareConfig
karta_configurations={
    # Disable a provider you don't want to use.
    "exclude_providers": [
        "wolfram_alpha_dispatcher_v1"
    ],
    
    # Force certain providers to be tried first for all queries.
    "priority_providers": [
        "private_rag_dispatcher_v1",
    ],
    
    # Guarantee a final fallback if the smart router finds no good options.
    "fallback_provider": "google_search_tool_v1",

    # Provide API keys and other specific configs
    "dispatcher_specific_configs": {
        "wolfram_alpha_dispatcher_v1": {
            "app_id": "YOUR-WOLFRAM-APP-ID"
        }
    }
}
```

## 4. Usage

Usage remains the same. The complexity is now handled internally by the `KnowledgeRouter`.

```python
# This query will be automatically routed to WolframAlpha by the router.
fact = await genie.karta.lookup_fact(entity="earth", attribute="mass")

# This query will be routed to Wikipedia or Wikidata.
fact = await genie.karta.lookup_fact(entity="France", attribute="capital")
```
