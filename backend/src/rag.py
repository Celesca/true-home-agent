from __future__ import annotations

import logging
from typing import Any

import chromadb

from config.settings import get_settings

_collection = None
logger = logging.getLogger(__name__)


def _get_collection():
    global _collection
    if _collection is not None:
        return _collection

    settings = get_settings()
    try:
        client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
        _collection = client.get_or_create_collection(name=settings.chroma_collection)
        return _collection
    except Exception:
        logger.exception("Unable to initialize ChromaDB collection")
        return None


def query_knowledge_base(query: str, limit: int = 4) -> dict[str, Any]:
    collection = _get_collection()
    if collection is None:
        return {"status": "unavailable", "reason": "chroma_not_reachable"}

    results = collection.query(query_texts=[query], n_results=limit)
    return {
        "status": "ok",
        "documents": results.get("documents", []),
        "metadatas": results.get("metadatas", []),
        "ids": results.get("ids", []),
    }


def upsert_documents(items: list[dict[str, Any]]) -> int:
    collection = _get_collection()
    if collection is None:
        return 0

    ids = [item["id"] for item in items]
    documents = [item["text"] for item in items]
    metadatas = [item.get("metadata") or {} for item in items]
    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    return len(items)
