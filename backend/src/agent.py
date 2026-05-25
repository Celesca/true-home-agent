from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

from config.prompts import BASE_SYSTEM_PROMPT, TOOL_MARKDOWN
from config.settings import get_settings
from src.models import ChatRequest, ToolCall
from src.tools import ALL_TOOLS, TOOLS_BY_INTENT


INTENT_KEYWORDS = {
    "trueid": ["trueid", "netflix", "sports", "movie", "stream"],
    "fiber": ["wifi", "fiber", "internet", "slow", "router", "latency"],
    "smart_home": ["pause", "device", "schedule", "electricity", "smart home"],
    "wallet": ["bill", "pay", "wallet", "balance", "transaction"],
}


def classify_intent(message: str) -> str:
    lowered = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(token in lowered for token in keywords):
            return intent
    return "rag"


def build_system_prompt(intent: str) -> tuple[str, list[str]]:
    tool_markdown = []
    if intent in TOOL_MARKDOWN:
        tool_markdown.append(TOOL_MARKDOWN[intent])
    if intent == "rag":
        tool_markdown.append(TOOL_MARKDOWN["rag"])
    system_prompt = BASE_SYSTEM_PROMPT
    if tool_markdown:
        system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n" + "\n\n".join(tool_markdown)
    return system_prompt, tool_markdown


def build_callbacks(household_id: str | None) -> list[Any]:
    settings = get_settings()
    if not settings.langfuse_public_key or not settings.langfuse_secret_key:
        return []
    try:
        from langfuse.callback import CallbackHandler
    except Exception:
        return []

    handler = CallbackHandler(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
        session_id=household_id,
    )
    return [handler]


def build_llm(callbacks: list[Any]) -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(model=settings.openai_model, temperature=0.2, callbacks=callbacks)


def select_tools(intent: str):
    if intent in TOOLS_BY_INTENT:
        return TOOLS_BY_INTENT[intent]
    return ALL_TOOLS


def extract_tool_calls(messages: list[Any]) -> list[ToolCall]:
    tool_calls: list[ToolCall] = []
    for message in messages:
        if isinstance(message, AIMessage) and message.tool_calls:
            for call in message.tool_calls:
                tool_calls.append(ToolCall(name=call.get("name", ""), arguments=call.get("args", {})))
    return tool_calls


def run_agent(request: ChatRequest) -> dict[str, Any]:
    intent = classify_intent(request.message)
    system_prompt, tool_markdown = build_system_prompt(intent)
    tools = select_tools(intent)
    callbacks = build_callbacks(request.household_id)

    llm = build_llm(callbacks)
    agent = create_react_agent(llm, tools)

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=request.message)]
    result = agent.invoke({"messages": messages}, config={"callbacks": callbacks})
    final_messages = result.get("messages", [])
    answer = final_messages[-1].content if final_messages else ""

    return {
        "intent": intent,
        "system_prompt": system_prompt,
        "tool_markdown": tool_markdown,
        "tool_calls": extract_tool_calls(final_messages),
        "trace": [
            {"node": "classify_intent", "detail": {"intent": intent}},
            {"node": "build_prompt", "detail": {"tool_markdown_count": len(tool_markdown)}},
            {"node": "react_agent", "detail": {"tool_count": len(tools)}},
        ],
        "answer": answer,
    }


def preview_prompt(request: ChatRequest) -> dict[str, Any]:
    intent = classify_intent(request.message)
    system_prompt, tool_markdown = build_system_prompt(intent)
    return {"intent": intent, "system_prompt": system_prompt, "tool_markdown": tool_markdown}
