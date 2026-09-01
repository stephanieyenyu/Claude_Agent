import os, json, httpx
from mcp.server.fastmcp import FastMCP
from starlette.routing import Route
from starlette.responses import PlainTextResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from mcp.server.transport_security import TransportSecuritySettings

REPLIES = "/tmp/replies.json"

mcp = FastMCP("line-push")
mcp.settings.streamable_http_path = "/mcp"
mcp.settings.transport_security = TransportSecuritySettings(
    allowed_hosts=["*"], allowed_origins=["*"]
)

@mcp.tool()
def push_line(text: str) -> str:
    """把訊息推播到我的 LINE。收件人固定，不能指定。"""
    r = httpx.post(
        "https://api.line.me/v2/bot/message/push",
        headers={"Authorization": f"Bearer {os.environ['LINE_TOKEN']}"},
        json={"to": os.environ["MY_USER_ID"],
              "messages": [{"type": "text", "text": text[:4900]}]},
    )
    return f"{r.status_code} {r.text}"

@mcp.tool()
def read_replies() -> str:
    """讀取我從 LINE 傳來、還沒處理的訊息。讀完會清空。"""
    try:
        with open(REPLIES) as f:
            msgs = json.load(f)
    except Exception:
        return "（沒有新訊息）"
    with open(REPLIES, "w") as f:
        json.dump([], f)
    return "\n".join(msgs) if msgs else "（沒有新訊息）"

async def webhook(request):
    body = await request.json()
    msgs = []
    try:
        with open(REPLIES) as f:
            msgs = json.load(f)
    except Exception:
        pass
    for e in body.get("events", []):
        if e.get("type") == "message" and e["message"].get("type") == "text":
            msgs.append(e["message"]["text"])
    with open(REPLIES, "w") as f:
        json.dump(msgs, f, ensure_ascii=False)
    return PlainTextResponse("OK")

app = mcp.streamable_http_app()
app.routes.append(Route("/webhook", webhook, methods=["POST"]))
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
