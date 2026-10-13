from dataclasses import dataclass

from fastapi import WebSocket


@dataclass(slots=True)
class Peer:
    public_key: bytes
    websocket: WebSocket

    async def send(self, data: bytes) -> None:
        await self.websocket.send_bytes(data)
