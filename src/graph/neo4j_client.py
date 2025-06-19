from typing import Any

class Neo4jClient:
    """Neo4j client stub."""
    def __init__(self, uri: str, user: str, password: str):
        # TODO: Initialize Neo4j driver
        pass

    def upsert_note(self, note: str, metadata: dict[str, Any]) -> None:
        # TODO: Upsert note and metadata into Neo4j
        pass 