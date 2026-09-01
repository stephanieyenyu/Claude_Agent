from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Mount

inner = mcp.streamable_http_app()

class FixHost(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request.scope["headers"] = [
            (b"host", b"localhost") if k == b"host" else (k, v)
            for k, v in request.scope["headers"]
        ]
        return await call_next(request)

app = Starlette(
    routes=[
        Route("/webhook", webhook, methods=["POST"]),
        Mount("/", app=inner),
    ],
    middleware=[Middleware(FixHost)],
)
