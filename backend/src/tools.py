from __future__ import annotations

from typing import Any
import random

from langchain_core.tools import tool

from src.rag import query_knowledge_base


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
    "subscriptions": [
        {
            "service": "TrueID Plus Family",
            "category": "Streaming",
            "price_thb": 249.00,
            "billing_cycle": "monthly",
            "status": "active",
            "owner": "Family",
            "next_bill_date": "2026-06-01",
        },
        {
            "service": "True Fiber 1Gbps",
            "category": "Home Internet",
            "price_thb": 899.00,
            "billing_cycle": "monthly",
            "status": "active",
            "owner": "Home",
            "next_bill_date": "2026-06-03",
        },
        {
            "service": "True Move H 5G Family",
            "category": "Mobile",
            "price_thb": 1199.00,
            "billing_cycle": "monthly",
            "status": "active",
            "owner": "Parents",
            "next_bill_date": "2026-06-05",
        },
    ],
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


@tool("check_balance")
def check_balance() -> dict[str, Any]:
    """Return current wallet balance and user name."""
    return {"balance_thb": DB["wallet"]["balance_thb"], "user": DB["wallet"]["user"]}


@tool("pay")
def pay(to: str, amount: float) -> dict[str, Any]:
    """Pay a biller or merchant and return the payment result."""
    if not to.strip() or amount <= 0:
        return {"status": "failed", "reason": "invalid_payment_request"}

    balance = DB["wallet"]["balance_thb"]
    if amount > balance:
        return {"status": "failed", "reason": "insufficient_funds", "balance_thb": balance}

    DB["wallet"]["balance_thb"] -= amount
    txn_id = f"T{random.randint(100, 999)}"
    DB["transactions"].append({"id": txn_id, "to": to, "amount": amount, "date": "2026-05-26"})
    return {"status": "success", "txn_id": txn_id, "new_balance_thb": DB["wallet"]["balance_thb"]}


@tool("get_transactions")
def get_transactions(limit: int = 5) -> dict[str, Any]:
    """Return recent wallet transactions."""
    return {"transactions": DB["transactions"][-limit:]}


@tool("get_pending_bills")
def get_pending_bills() -> dict[str, Any]:
    """Return unpaid bills due this month."""
    return {"pending_bills": DB["billers"]}


@tool("get_trueid_subscription")
def get_trueid_subscription() -> dict[str, Any]:
    """Return the current TrueID subscription details."""
    return DB["trueid"]


@tool("list_family_subscriptions")
def list_family_subscriptions() -> dict[str, Any]:
    """Return all family subscription records."""
    return {"subscriptions": DB["subscriptions"]}


@tool("check_content_entitlement")
def check_content_entitlement(content: str) -> dict[str, Any]:
    """Check whether the requested content is included in the current plan."""
    title = content.lower()
    if "sports" in title:
        return {"content": content, "included": DB["trueid"]["sports"]}
    if "netflix" in title:
        return {"content": content, "included": DB["trueid"]["netflix_bundle"]}
    return {"content": content, "included": True}


@tool("recommend_trueid_plan")
def recommend_trueid_plan(preference: str) -> dict[str, Any]:
    """Recommend a TrueID plan based on user preference."""
    if "cheap" in preference.lower():
        return {"recommended_plan": "TrueID Basic", "reason": "lowest cost while preserving core streaming access"}
    return {"recommended_plan": DB["trueid"]["plan"], "reason": "preserves sports and bundled streaming"}


@tool("check_network_status")
def check_network_status() -> dict[str, Any]:
    """Return the current fiber network status."""
    return DB["fiber"]


@tool("diagnose_wifi_issue")
def diagnose_wifi_issue(room: str) -> dict[str, Any]:
    """Diagnose Wi-Fi issues for a room and return a likely cause."""
    return {
        "room": room,
        "likely_cause": "coverage_or_interference",
        "signal_strength": DB["fiber"]["signal_strength"],
        "latency_ms": DB["fiber"]["latency_ms"],
    }


@tool("recommend_mesh_upgrade")
def recommend_mesh_upgrade() -> dict[str, Any]:
    """Recommend a mesh upgrade when coverage is inconsistent."""
    return {"recommended": True, "reason": "consistent coverage across bedrooms and child devices"}


@tool("list_devices")
def list_devices() -> dict[str, Any]:
    """List household devices connected to the network."""
    return {"devices": DB["devices"]}


@tool("pause_device")
def pause_device(device_name: str) -> dict[str, Any]:
    """Pause a device by name."""
    for device in DB["devices"]:
        if device["name"].lower() == device_name.lower():
            device["status"] = "paused"
            return {"status": "success", "device": device}
    return {"status": "not_found", "device_name": device_name}


@tool("create_schedule")
def create_schedule(device_name: str, action: str, time: str) -> dict[str, Any]:
    """Create a simple device schedule rule."""
    return {"status": "scheduled", "device_name": device_name, "action": action, "time": time}


@tool("search_knowledge_base")
def search_knowledge_base(query: str, limit: int = 4) -> dict[str, Any]:
    """Search the household knowledge base via ChromaDB."""
    return query_knowledge_base(query=query, limit=limit)


TOOLS_BY_INTENT = {
    "subscription": [list_family_subscriptions],
    "wallet": [check_balance, get_transactions, get_pending_bills, pay],
    "trueid": [get_trueid_subscription, check_content_entitlement, recommend_trueid_plan],
    "fiber": [check_network_status, diagnose_wifi_issue, recommend_mesh_upgrade],
    "smart_home": [list_devices, pause_device, create_schedule],
    "rag": [search_knowledge_base],
}


ALL_TOOLS = [
    list_family_subscriptions,
    check_balance,
    get_transactions,
    get_pending_bills,
    pay,
    get_trueid_subscription,
    check_content_entitlement,
    recommend_trueid_plan,
    check_network_status,
    diagnose_wifi_issue,
    recommend_mesh_upgrade,
    list_devices,
    pause_device,
    create_schedule,
    search_knowledge_base,
]
