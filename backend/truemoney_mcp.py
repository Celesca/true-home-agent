"""Mock True Home AI backend.

This file provides a FastAPI app, a lightweight LangGraph-style pipeline,
intent routing, and mocked household tools so the frontend can be built later
against a stable backend contract.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Literal
import random

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(title="True Home AI Agent", version="0.1.0")


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


DB = {
    "wallet": {"balance_thb": 2340.50, "user": "Somchai K."},
    "transactions": [
        {"id": "T001", "to": "MEA Electric", "amount": 890, "date": "2026-05-20"},
        {"id": "T002", "to": "7-Eleven", "amount": 145, "date": "2026-05-22"},
        {"id": "T003", "to": "True Move H", "amount": 299, "date": "2026-05-24"},
    ],
    "billers": {
        "MEA Electric": 1150.00,
        "PWA Water": 230.00,
        "True Move H": 299.00,
    },
    "trueid": {
        "plan": "TrueID Plus Family",
        "sports": True,
        "netflix_bundle": True,
        "price_thb": 249.00,
    },
    "fiber": {
        "status": "degraded",
        "latency_ms": 78,
        "signal_strength": "medium",
        "last_outage": "2026-05-25 19:20",
    },
    "devices": [
        {"name": "Bedroom TV", "status": "online", "group": "children"},
        {"name": "Child Tablet", "status": "online", "group": "children"},
        {"name": "Living Room Speaker", "status": "paused", "group": "family"},
    ],
}


SYSTEM_PROMPT = """You are True Home AI Agent, a bilingual Thai-English household assistant for True customers.

Your job is to understand the user’s household goal, identify the correct intent, and either answer directly or use the available tools in the safest and most helpful way.

Operating rules:
- Always respond in the user’s preferred language when possible, and switch smoothly between Thai and English when helpful.
- Prefer action-oriented answers: diagnose, explain, compare, recommend, or prepare a support step.
- If a tool is needed, choose the smallest tool set that solves the request.
- If the request is ambiguous, ask one focused clarifying question.
- Never invent account, billing, subscription, device, or network data.
- If the issue cannot be resolved automatically, summarize the evidence and escalate cleanly.

Household priorities:
- Connectivity first: router, Wi-Fi, Fiber, device performance, outages, and service status.
- Family planning: subscriptions, bundles, bill optimization, package changes, and savings.
- Content access: TrueID, streaming, sports, and household viewing rules.
- Safety and control: parental rules, device pauses, smart home automation, and electricity saving.

When tool evidence is available:
- Explain what was checked.
- State the likely cause or best next step.
- Mention any tradeoffs before recommending a plan or change.

When giving a final answer:
- Be concise.
- Use bullets only when they improve readability.
- End with a clear next action when possible."""


TOOL_MARKDOWN = {
    "wallet": """## Tool Pack: TrueMoney Wallet

Use this pack when the user asks about balance, bills, payments, spending, or wallet-linked subscriptions.

Available tools:
- check_balance
- get_transactions
- get_pending_bills
- pay

Response style:
- Show the amount, the target, and the consequence of the action.
- If funds are insufficient, explain the shortfall and propose the safest fallback.""",
    "trueid": """## Tool Pack: TrueID

Use this pack when the user asks about TrueID subscriptions, sports, streaming access, login issues, content entitlement, or package compatibility.

Available tools:
- get_trueid_subscription
- check_content_entitlement
- recommend_trueid_plan

Response style:
- Explain whether the request is a subscription issue, entitlement issue, or login issue.
- Recommend only plans that preserve the user’s stated must-have content.""",
    "fiber": """## Tool Pack: True Fiber

Use this pack when the user asks about slow internet, router trouble, outages, mesh Wi-Fi, or home-network diagnostics.

Available tools:
- check_network_status
- diagnose_wifi_issue
- recommend_mesh_upgrade

Response style:
- Explain whether the likely root cause is service-side, router-side, or device-side.
- Give the user one immediate fix and one longer-term recommendation.""",
    "smart_home": """## Tool Pack: Smart Home

Use this pack when the user asks to pause devices, automate schedules, save electricity, or manage household device access.

Available tools:
- list_devices
- pause_device
- create_schedule

Response style:
- Confirm the target device and the timing before making a change.
- If the action affects a child device or family rule, describe the policy clearly.""",
}


def check_balance() -> dict[str, Any]:
    return {"balance_thb": DB["wallet"]["balance_thb"], "user": DB["wallet"]["user"]}


def pay(to: str, amount: float) -> dict[str, Any]:
    balance = DB["wallet"]["balance_thb"]
    if amount > balance:
        return {"status": "failed", "reason": "insufficient_funds", "balance_thb": balance}

    DB["wallet"]["balance_thb"] -= amount
    txn_id = f"T{random.randint(100, 999)}"
    DB["transactions"].append({"id": txn_id, "to": to, "amount": amount, "date": "2026-05-26"})
    return {"status": "success", "txn_id": txn_id, "new_balance_thb": DB["wallet"]["balance_thb"]}


def get_transactions(limit: int = 5) -> dict[str, Any]:
    return {"transactions": DB["transactions"][-limit:]}


def get_pending_bills() -> dict[str, Any]:
    return {"pending_bills": DB["billers"]}


def get_trueid_subscription() -> dict[str, Any]:
    return DB["trueid"]


def check_content_entitlement(content: str) -> dict[str, Any]:
    title = content.lower()
    if "sports" in title:
        return {"content": content, "included": DB["trueid"]["sports"]}
    if "netflix" in title:
        return {"content": content, "included": DB["trueid"]["netflix_bundle"]}
    return {"content": content, "included": True}


def recommend_trueid_plan(preference: str) -> dict[str, Any]:
    if "cheap" in preference.lower():
        return {"recommended_plan": "TrueID Basic", "reason": "lowest cost while preserving core streaming access"}
    return {"recommended_plan": DB["trueid"]["plan"], "reason": "preserves sports and bundled streaming"}


def check_network_status() -> dict[str, Any]:
    return DB["fiber"]


def diagnose_wifi_issue(room: str) -> dict[str, Any]:
    return {
        "room": room,
        "likely_cause": "coverage_or_interference",
        "signal_strength": DB["fiber"]["signal_strength"],
        "latency_ms": DB["fiber"]["latency_ms"],
    }


def recommend_mesh_upgrade() -> dict[str, Any]:
    return {"recommended": True, "reason": "consistent coverage across bedrooms and child devices"}


def list_devices() -> dict[str, Any]:
    return {"devices": DB["devices"]}


def pause_device(device_name: str) -> dict[str, Any]:
    for device in DB["devices"]:
        if device["name"].lower() == device_name.lower():
            device["status"] = "paused"
            return {"status": "success", "device": device}
    return {"status": "not_found", "device_name": device_name}


def create_schedule(device_name: str, action: str, time: str) -> dict[str, Any]:
    return {"status": "scheduled", "device_name": device_name, "action": action, "time": time}


MOCK_TOOLS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "check_balance": lambda _: check_balance(),
    "pay": lambda payload: pay(payload["to"], payload["amount"]),
    "get_transactions": lambda payload: get_transactions(payload.get("limit", 5)),
    "get_pending_bills": lambda _: get_pending_bills(),
    "get_trueid_subscription": lambda _: get_trueid_subscription(),
    "check_content_entitlement": lambda payload: check_content_entitlement(payload["content"]),
    "recommend_trueid_plan": lambda payload: recommend_trueid_plan(payload["preference"]),
    "check_network_status": lambda _: check_network_status(),
    "diagnose_wifi_issue": lambda payload: diagnose_wifi_issue(payload["room"]),
    "recommend_mesh_upgrade": lambda _: recommend_mesh_upgrade(),
    "list_devices": lambda _: list_devices(),
    "pause_device": lambda payload: pause_device(payload["device_name"]),
    "create_schedule": lambda payload: create_schedule(payload["device_name"], payload["action"], payload["time"]),
}


class MockLangGraph:
    def __init__(self) -> None:
        self.nodes = [
            self.classify_intent,
            self.assemble_prompt,
            self.plan_tools,
            self.execute_tools,
            self.draft_answer,
        ]

    def run(self, request: ChatRequest) -> dict[str, Any]:
        state: dict[str, Any] = {"request": request.model_dump(), "trace": []}
        for node in self.nodes:
            state = node(state)
        return state

    def classify_intent(self, state: dict[str, Any]) -> dict[str, Any]:
        message = state["request"]["message"].lower()
        if any(token in message for token in ["trueid", "netflix", "sports", "movie", "stream"]):
            intent = "trueid"
        elif any(token in message for token in ["wifi", "fiber", "internet", "slow", "router", "latency"]):
            intent = "fiber"
        elif any(token in message for token in ["pause", "device", "schedule", "electricity", "smart home"]):
            intent = "smart_home"
        elif any(token in message for token in ["bill", "pay", "wallet", "balance", "transaction"]):
            intent = "wallet"
        else:
            intent = "general"

        state["intent"] = intent
        state["trace"].append({"node": "classify_intent", "detail": {"intent": intent}})
        return state

    def assemble_prompt(self, state: dict[str, Any]) -> dict[str, Any]:
        intent = state["intent"]
        markdown_blocks = []
        if intent in TOOL_MARKDOWN:
            markdown_blocks.append(TOOL_MARKDOWN[intent])

        state["system_prompt"] = SYSTEM_PROMPT
        state["tool_markdown"] = markdown_blocks
        state["trace"].append({"node": "assemble_prompt", "detail": {"tool_markdown_count": len(markdown_blocks)}})
        return state

    def plan_tools(self, state: dict[str, Any]) -> dict[str, Any]:
        intent = state["intent"]
        message = state["request"]["message"].lower()

        planned: list[ToolCall] = []
        if intent == "wallet":
            if "balance" in message:
                planned.append(ToolCall(name="check_balance"))
            if any(token in message for token in ["bill", "bills"]):
                planned.append(ToolCall(name="get_pending_bills"))
        elif intent == "trueid":
            planned.append(ToolCall(name="get_trueid_subscription"))
            if any(token in message for token in ["sports", "netflix", "movie"]):
                planned.append(ToolCall(name="check_content_entitlement", arguments={"content": message}))
        elif intent == "fiber":
            planned.append(ToolCall(name="check_network_status"))
            planned.append(ToolCall(name="diagnose_wifi_issue", arguments={"room": self._infer_room(message)}))
        elif intent == "smart_home":
            planned.append(ToolCall(name="list_devices"))
            if any(token in message for token in ["pause", "turn off"]):
                planned.append(ToolCall(name="pause_device", arguments={"device_name": self._infer_device(message)}))

        state["tool_calls"] = planned
        state["trace"].append({"node": "plan_tools", "detail": {"tool_calls": [tool.model_dump() for tool in planned]}})
        return state

    def execute_tools(self, state: dict[str, Any]) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for tool_call in state.get("tool_calls", []):
            runner = MOCK_TOOLS.get(tool_call.name)
            if runner is None:
                raise HTTPException(status_code=400, detail=f"Unsupported tool: {tool_call.name}")
            result = runner(tool_call.arguments)
            results.append({"tool": tool_call.name, "arguments": tool_call.arguments, "result": result})

        state["tool_results"] = results
        state["trace"].append({"node": "execute_tools", "detail": {"results_count": len(results)}})
        return state

    def draft_answer(self, state: dict[str, Any]) -> dict[str, Any]:
        intent = state["intent"]
        if intent == "wallet":
            answer = self._draft_wallet_answer(state)
        elif intent == "trueid":
            answer = self._draft_trueid_answer(state)
        elif intent == "fiber":
            answer = self._draft_fiber_answer(state)
        elif intent == "smart_home":
            answer = self._draft_smart_home_answer(state)
        else:
            answer = "I can help with True billing, TrueID, True Fiber, and home-device workflows. Tell me which household problem you want to solve."

        state["answer"] = answer
        state["trace"].append({"node": "draft_answer", "detail": {"answer_type": intent}})
        return state

    def _infer_room(self, message: str) -> str:
        for room in ["bedroom", "living room", "kitchen", "office"]:
            if room in message:
                return room
        return "home"

    def _infer_device(self, message: str) -> str:
        for device in ["child tablet", "bedroom tv", "living room speaker"]:
            if device in message:
                return device.title()
        return "Unknown device"

    def _draft_wallet_answer(self, state: dict[str, Any]) -> str:
        balance = DB["wallet"]["balance_thb"]
        pending = DB["billers"]
        return f"Current wallet balance is THB {balance:.2f}. Pending bills this month: {', '.join(f'{name} THB {amount:.2f}' for name, amount in pending.items())}."

    def _draft_trueid_answer(self, state: dict[str, Any]) -> str:
        plan = DB["trueid"]
        return (
            f"Your current TrueID plan is {plan['plan']} at THB {plan['price_thb']:.2f}. "
            f"Sports included: {'yes' if plan['sports'] else 'no'}. Netflix bundle included: {'yes' if plan['netflix_bundle'] else 'no'}."
        )

    def _draft_fiber_answer(self, state: dict[str, Any]) -> str:
        fiber = DB["fiber"]
        return (
            f"Network status looks {fiber['status']} with latency around {fiber['latency_ms']} ms and {fiber['signal_strength']} signal strength. "
            "The likely cause is coverage or interference, so the fastest fix is to move closer to the router or test another room."
        )

    def _draft_smart_home_answer(self, state: dict[str, Any]) -> str:
        return "I found the household devices and can pause, schedule, or limit access once you confirm the exact target device and time."


GRAPH = MockLangGraph()


def select_tool_markdown(intent: str) -> list[str]:
    if intent == "trueid":
        return [TOOL_MARKDOWN["trueid"]]
    if intent == "fiber":
        return [TOOL_MARKDOWN["fiber"]]
    if intent == "smart_home":
        return [TOOL_MARKDOWN["smart_home"]]
    if intent == "wallet":
        return [TOOL_MARKDOWN["wallet"]]
    return []


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "true-home-ai-agent", "timestamp": datetime.utcnow().isoformat()}


@app.get("/tools")
def tools() -> dict[str, Any]:
    return {"tools": list(MOCK_TOOLS.keys())}


@app.post("/agent/run", response_model=ChatResponse)
def run_agent(request: ChatRequest) -> ChatResponse:
    state = GRAPH.run(request)
    return ChatResponse(
        intent=state["intent"],
        system_prompt=state["system_prompt"],
        tool_markdown=state["tool_markdown"],
        tool_calls=state.get("tool_calls", []),
        trace=[AgentTraceStep(**step) for step in state["trace"]],
        answer=state["answer"],
    )


@app.post("/agent/preview")
def preview_prompt(request: ChatRequest) -> dict[str, Any]:
    intent = GRAPH.classify_intent({"request": request.model_dump(), "trace": []})["intent"]
    return {
        "intent": intent,
        "system_prompt": SYSTEM_PROMPT,
        "tool_markdown": select_tool_markdown(intent),
    }


@app.get("/mock-data")
def mock_data() -> dict[str, Any]:
    return DB