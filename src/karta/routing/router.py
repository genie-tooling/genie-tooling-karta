# karta-engine/src/karta/routing/router.py

import logging
from typing import Any, AsyncIterable, Dict, List, Tuple

from genie_tooling.core.types import Chunk
from karta.dispatchers.abc import KnowledgeProvider

logger = logging.getLogger(__name__)


class KnowledgeRouter:
    """Intelligently routes a knowledge query by using the core framework's embedding and vector store services."""

    def __init__(
        self,
        plugin_manager: Any,
        embedder: Any,
        vector_store: Any,
        config: Dict[str, Any],
    ):
        """
        Initializes the router with injected dependencies from the core framework.

        Args:
            plugin_manager: The core plugin manager.
            embedder: The core embedding provider.
            vector_store: The core vector store provider (e.g., from the RAG facade).
            config: The configuration for the router.
        """
        self.plugin_manager = plugin_manager
        self.embedder = embedder
        self.vector_store = vector_store
        self.config = config
        self.provider_map: List[Tuple[str, str]] = []  # (plugin_id, description)
        self.is_ready = False
        self.collection_name = self.config.get(
            "collection_name", "karta_knowledge_providers"
        )

    async def setup(self):
        """Discovers knowledge providers and adds their descriptions to the vector store."""
        logger.info(
            "KnowledgeRouter setup: Discovering and indexing knowledge providers..."
        )

        all_knowledge_providers = (
            await self.plugin_manager.get_all_plugin_instances_by_type(KnowledgeProvider)
        )

        exclude_list = self.config.get("exclude_providers", [])

        for plugin_instance in all_knowledge_providers:
            # Get config for this specific dispatcher from the router's main config
            dispatcher_config = self.config.get("dispatcher_specific_configs", {}).get(
                plugin_instance.plugin_id, {}
            )
            # Pass this specific config to the plugin's setup method.
            await plugin_instance.setup(dispatcher_config)

            if plugin_instance.plugin_id in exclude_list:
                continue
            description = plugin_instance.knowledge_description
            if description:
                self.provider_map.append((plugin_instance.plugin_id, description))

        if not self.provider_map:
            logger.warning("No knowledge providers found to index.")
            return

        async def _provider_chunks() -> AsyncIterable[Chunk]:
            """Helper async generator to create Chunk objects for the embedder."""

            class ProviderChunk(Chunk):
                def __init__(self, _id, _content):
                    self.id = _id
                    self.content = _content
                    self.metadata = {}

            for plugin_id, desc in self.provider_map:
                yield ProviderChunk(plugin_id, desc)

        try:
            # FIX: Await the embedder call to get the async generator.
            embedding_stream = await self.embedder.embed(chunks=_provider_chunks())
            await self.vector_store.add(
                embeddings=embedding_stream,
                config={"collection_name": self.collection_name},
            )
            self.is_ready = True
            logger.info(
                f"KnowledgeRouter indexed {len(self.provider_map)} providers into collection '{self.collection_name}'."
            )
        except Exception as e:
            logger.error(
                f"Failed to index knowledge providers in vector store: {e}",
                exc_info=True,
            )
            self.is_ready = False

    async def get_provider_cascade(self, query: str, top_k: int = 5) -> List[str]:
        if not self.is_ready:
            return (
                [self.config.get("fallback_provider")]
                if self.config.get("fallback_provider")
                else []
            )

        class QueryChunk(Chunk):
            def __init__(self, content):
                self.id = "query"
                self.content = content
                self.metadata = {}

        async def query_chunk_generator() -> AsyncIterable[Chunk]:
            yield QueryChunk(query)

        try:
            # FIX: Await the embedder call to get the async generator.
            query_embedding_stream = await self.embedder.embed(
                chunks=query_chunk_generator()
            )
            query_embedding_result = [res async for res in query_embedding_stream]
        except Exception as e:
            logger.error(f"Error getting query embedding: {e}", exc_info=True)
            query_embedding_result = []

        if not query_embedding_result:
            logger.warning("Could not generate embedding for query.")
            return []
        query_vector = query_embedding_result[0][1]

        search_results = await self.vector_store.search(
            query_embedding=query_vector,
            top_k=min(top_k, len(self.provider_map)),
            config={"collection_name": self.collection_name},
        )
        ranked_ids = [chunk.id for chunk in search_results if chunk.id]

        priority_list = self.config.get("priority_providers", [])
        final_cascade = list(dict.fromkeys(priority_list + ranked_ids))
        fallback = self.config.get("fallback_provider")
        if fallback and fallback not in final_cascade:
            final_cascade.append(fallback)

        logger.debug(f"Knowledge cascade for query '{query}': {final_cascade}")
        return final_cascade