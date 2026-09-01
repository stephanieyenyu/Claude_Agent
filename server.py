import os, httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("line-push",
              host="0.0.0.0",
              port=int(os.environ.get("PORT", 8000)),
              streamable_http_path="/mcp-steph2475")

@mcp.tool()
def push_line(text: str) -> str:
    """把今日待辦推播到我的 LINE。收件人固定，不能指定。"""
    r = httpx.post(
        "https://api.line.me/v2/bot/message/push",
        headers={"Authorization": f"Bearer {os.environ['LINE_TOKEN']}"},
        json={"to": os.environ["MY_USER_ID"],
              "messages": [{"type": "text", "text": text[:4900]}]},
    )
    return f"{r.status_code} {r.text}"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
