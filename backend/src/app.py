from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException

from src.agent import preview_prompt, run_agent
from src.models import ChatRequest, ChatResponse, RagUpsertRequest, RagUpsertResponse
from src.rag import upsert_documents
from src.tools import ALL_TOOLS


app = FastAPI(title="True Home AI Agent", version="0.2.0")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "true-home-ai-agent", "timestamp": datetime.utcnow().isoformat()}


@app.get("/tools")
def tools() -> dict[str, Any]:
    return {"tools": [tool.name for tool in ALL_TOOLS]}


@app.post("/agent/preview")
def agent_preview(request: ChatRequest) -> dict[str, Any]:
    return preview_prompt(request)


@app.post("/agent/run", response_model=ChatResponse)
def agent_run(request: ChatRequest) -> ChatResponse:
    try:
        state = run_agent(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(
        intent=state["intent"],
        system_prompt=state["system_prompt"],
        tool_markdown=state["tool_markdown"],
        tool_calls=state["tool_calls"],
        trace=state["trace"],
        answer=state["answer"],
    )


@app.post("/rag/upsert", response_model=RagUpsertResponse)
def rag_upsert(request: RagUpsertRequest) -> RagUpsertResponse:
    items = [item.model_dump() for item in request.items]
    count = upsert_documents(items)
    if count == 0:
        raise HTTPException(status_code=503, detail="ChromaDB is not reachable")
    return RagUpsertResponse(count=count)
