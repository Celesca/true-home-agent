from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    language: Literal["th", "en", "auto"] = "auto"
    household_id: str | None = None


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentTraceStep(BaseModel):
    node: str
    detail: dict[str, Any]


class ChatResponse(BaseModel):
    intent: str
    system_prompt: str
    tool_markdown: list[str]
    tool_calls: list[ToolCall]
    trace: list[AgentTraceStep]
    answer: str


class RagUpsertItem(BaseModel):
    id: str
    text: str
    metadata: dict[str, Any] | None = None


class RagUpsertRequest(BaseModel):
    items: list[RagUpsertItem]


class RagUpsertResponse(BaseModel):
    count: int
