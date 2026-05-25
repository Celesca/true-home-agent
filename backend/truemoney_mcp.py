# TrueMoney MCP Server — mock tool definitions
# Paste this into Colab Cell 1. That's it.

import anthropic, json, random

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

# ── Mock database ────────────────────────────────────────────────
DB = {
    "wallet": {"balance_thb": 2340.50, "user": "Somchai K."},
    "transactions": [
        {"id": "T001", "to": "MEA Electric",  "amount": 890,  "date": "2026-05-20"},
        {"id": "T002", "to": "7-Eleven",     "amount": 145,  "date": "2026-05-22"},
        {"id": "T003", "to": "True Move H",  "amount": 299,  "date": "2026-05-24"},
    ],
    "billers": {
        "MEA Electric": 1150.00,
        "PWA Water":    230.00,
        "True Move H":  299.00,
    }
}

# ── Tool implementations ─────────────────────────────────────────
def check_balance() -> dict:
    """Return current wallet balance."""
    return {"balance_thb": DB["wallet"]["balance_thb"], "user": DB["wallet"]["user"]}

def pay(to: str, amount: float) -> dict:
    """Execute a payment. Returns success/failure with new balance."""
    bal = DB["wallet"]["balance_thb"]
    if amount > bal:
        return {"status": "failed", "reason": "insufficient_funds", "balance_thb": bal}
    DB["wallet"]["balance_thb"] -= amount
    txn_id = f"T{random.randint(100,999)}"
    DB["transactions"].append({"id": txn_id, "to": to, "amount": amount, "date": "2026-05-26"})
    return {"status": "success", "txn_id": txn_id, "new_balance_thb": DB["wallet"]["balance_thb"]}

def get_transactions(limit: int = 5) -> dict:
    """Return recent transaction history."""
    return {"transactions": DB["transactions"][-limit:]}

def get_pending_bills() -> dict:
    """Return bills due this month."""
    return {"pending_bills": DB["billers"]}

# ── MCP tool schemas (what Claude sees) ─────────────────────────
TOOLS = [
    {
        "name": "check_balance",
        "description": "Check the user's TrueMoney wallet balance.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "pay",
        "description": "Pay a merchant or biller from TrueMoney wallet.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to":     {"type": "string", "description": "Recipient name or biller ID"},
                "amount":{"type": "number", "description": "Amount in Thai Baht"}
            },
            "required": ["to", "amount"]
        }
    },
    {
        "name": "get_transactions",
        "description": "Fetch recent TrueMoney transaction history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of transactions to return"}
            },
            "required": []
        }
    },
    {
        "name": "get_pending_bills",
        "description": "Get all unpaid bills due this month.",
        "input_schema": {"type": "object", "properties": {}, "required": []}
    },
]

# ── Tool dispatcher ──────────────────────────────────────────────
def dispatch(tool_name: str, tool_input: dict) -> str:
    """Route Claude's tool call to the right function."""
    fns = {
        "check_balance":    lambda _: check_balance(),
        "pay":              lambda i: pay(i["to"], i["amount"]),
        "get_transactions": lambda i: get_transactions(i.get("limit", 5)),
        "get_pending_bills":lambda _: get_pending_bills(),
    }
    result = fns[tool_name](tool_input)
    return json.dumps(result)

# ── Agent loop ───────────────────────────────────────────────────
def run_agent(user_query: str) -> str:
    """Run TrueMoney agent until it reaches a final answer."""
    messages = [{"role": "user", "content": user_query}]
    while True:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )
        if resp.stop_reason == "end_turn":
            return resp.content[0].text
        # Claude wants to call a tool
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"  → calling {block.name}({block.input})")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": dispatch(block.name, block.input),
                })
        messages += [
            {"role": "assistant", "content": resp.content},
            {"role": "user",      "content": tool_results},
        ]

# ── Run it ───────────────────────────────────────────────────────
for query in [
    "จ่ายบิลค่าไฟและค่าน้ำทั้งหมดให้หน่อย แล้วบอกว่าเหลือเงินเท่าไหร่",
    "Do I have enough to pay all my bills this month?",
]:
    print(f"\nQuery: {query}")
    print(f"Answer: {run_agent(query)}")