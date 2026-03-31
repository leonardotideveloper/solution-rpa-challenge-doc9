import ssl

import websockets


def create_ssl_context() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


async def connect_websocket(
    url: str, timeout: int = 30
) -> websockets.WebSocketClientProtocol:
    ssl_ctx = create_ssl_context()
    return await websockets.connect(
        url,
        ssl=ssl_ctx,
        open_timeout=timeout,
        close_timeout=timeout,
    )
