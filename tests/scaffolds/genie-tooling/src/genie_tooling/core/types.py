# Functional Scaffold
from typing import Protocol, Any
class Plugin(Protocol):
    plugin_id: str
    async def setup(self, **kwargs: Any) -> None: ...
