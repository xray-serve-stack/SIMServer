import asyncio
import secrets
import base64
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from simserver import logging
from .peer_watch_manager import PeerWatchManager
from .crypto import (
    RESERVED_KEY,
    decrypt_payload,
    derive_peer_key,
    encrypt_payload,
)
from .message_definitions import (
    AUTHENTICATE,
    PEER_OFFLINE,
    PEER_ONLINE,
    REGISTER,
    WATCH_PEERS,
)
from .protocol import PeerRole
from .message_registry import MessageRegistry
from .packet import Packet
from .payload_pipeline import PayloadPipeline
from .peer import Peer
from .peer_manager import PeerManager


class SIMServer:
    def __init__(self) -> None:
        self.app = FastAPI()

        self.peer_watch_manager = PeerWatchManager()

        self.message_registry = MessageRegistry(
            definitions=(
                REGISTER,
                AUTHENTICATE,
                WATCH_PEERS,
                PEER_ONLINE,
                PEER_OFFLINE,
            )
        )

        self.server_private_key = X25519PrivateKey.generate()
        self.server_public_key = self.server_private_key.public_key()

        self.peer_manager = PeerManager()

        self.pipeline = PayloadPipeline(
            peer_role=PeerRole.SERVER,
        )

        self.app.websocket("/ws")(self.peer)

    async def peer(
        self,
        websocket: WebSocket,
    ) -> None:
        await websocket.accept()

        public_key: bytes | None = None

        try:
            public_key = await self.establish_peer(
                websocket,
            )

            peer = Peer(
                public_key=public_key,
                websocket=websocket,
            )

            self.peer_manager.add(peer)

            logging.info(f"[PEER] connected: {base64.b64encode(public_key).decode()}")

            for follower in self.peer_watch_manager.get_followers(
                public_key,
            ):
                follower_peer = self.peer_manager.get(follower)

                if follower_peer is None:
                    continue

                await self.send_peer_status(
                    peer=follower_peer,
                    target=public_key,
                    is_online=True,
                )

            while True:
                data = await websocket.receive_bytes()

                await self.handle_packet(
                    sender=peer,
                    data=data,
                )

        except WebSocketDisconnect:
            if public_key:
                logging.info(f"[PEER] disconnected: {base64.b64encode(public_key).decode()}")
            else:
                logging.debug("[PEER] disconnected, without auth.")

        except Exception as exc:
            logging.warning(f"[PEER] error: {exc}")

        finally:
            if public_key is not None:
                followers = self.peer_watch_manager.disconnect(
                    public_key,
                )

                self.peer_manager.remove(
                    public_key,
                )

                for follower in followers:
                    follower_peer = self.peer_manager.get(follower)

                    if follower_peer is None:
                        continue

                    await self.send_peer_status(
                        peer=follower_peer,
                        target=public_key,
                        is_online=False,
                    )

    async def establish_peer(
        self,
        websocket: WebSocket,
    ) -> bytes:
        pipeline = PayloadPipeline(
            peer_role=PeerRole.SERVER,
        )

        try:
            data = await asyncio.wait_for(
                websocket.receive_bytes(),
                timeout=10.0,
            )
        except asyncio.TimeoutError as exc:
            raise ValueError("Registration timeout") from exc

        packet = Packet.decode(data)

        if packet.peer != RESERVED_KEY:
            raise ValueError("Expected server registration packet")

        definition = self.message_registry.get(
            packet.message_type,
        )

        if definition is None or definition is not REGISTER:
            raise ValueError("Expected REGISTER message")

        register_payload = pipeline.receive(
            definition,
            packet.payload,
        )

        peer_public_key_bytes = register_payload["public_key"]

        peer_public_key = X25519PublicKey.from_public_bytes(
            peer_public_key_bytes,
        )

        peer_key = derive_peer_key(
            self.server_private_key,
            peer_public_key,
        )

        aad = AUTHENTICATE.id.to_bytes(
            8,
            "big",
        )

        pipeline.set_encryption(
            encrypt=lambda payload: encrypt_payload(
                key=peer_key,
                payload=payload,
                aad=aad,
            ),
            decrypt=lambda payload: decrypt_payload(
                key=peer_key,
                payload=payload,
                aad=aad,
            ),
        )

        nonce = secrets.token_bytes(32)

        authenticate_payload = pipeline.send(
            AUTHENTICATE,
            {
                "nonce": nonce,
            },
        )

        server_public_key = self.server_public_key.public_bytes(
            Encoding.Raw,
            PublicFormat.Raw,
        )

        authenticate_packet = Packet(
            peer=server_public_key,
            message_type=AUTHENTICATE.id,
            payload=authenticate_payload,
        )

        await websocket.send_bytes(
            authenticate_packet.encode(),
        )

        try:
            data = await asyncio.wait_for(
                websocket.receive_bytes(),
                timeout=10.0,
            )
        except asyncio.TimeoutError as exc:
            raise ValueError("Authentication timeout") from exc

        response = Packet.decode(data)

        if response.peer != RESERVED_KEY:
            raise ValueError("Expected server authentication response")

        if response.message_type != AUTHENTICATE.id:
            raise ValueError("Expected AUTHENTICATE response")

        response_payload = AUTHENTICATE.payload_codec.parse(
            PeerRole.SERVER,
            response.payload,
        )

        response_nonce = response_payload["nonce"]

        if response_nonce != nonce:
            raise ValueError("Invalid authentication response")

        return peer_public_key_bytes

    async def handle_packet(
        self,
        sender: Peer,
        data: bytes,
    ) -> None:
        packet = Packet.decode(data)

        if packet.peer == RESERVED_KEY:
            await self.handle_server_packet(
                sender=sender,
                packet=packet,
            )
            return

        await self.route_packet(
            sender=sender,
            packet=packet,
        )

    async def route_packet(
        self,
        sender: Peer,
        packet: Packet,
    ) -> None:
        peer = self.peer_manager.get(
            packet.peer,
        )

        if peer is None:
            logging.debug(
                f"[ROUTER] type={packet.message_type} peer offline: {base64.b64encode(packet.peer).decode()}"
            )
            return

        routed_packet = Packet(
            peer=sender.public_key,
            message_type=packet.message_type,
            payload=packet.payload,
        )

        await peer.send(
            routed_packet.encode(),
        )

        logging.debug(
            f"[ROUTER] "
            f"type={packet.message_type} "
            f"{base64.b64encode(sender.public_key).decode()} "
            f"-> {base64.b64encode(packet.peer).decode()}"
        )

    async def handle_server_packet(
        self,
        sender: Peer,
        packet: Packet,
    ) -> None:
        if packet.message_type in (
            REGISTER.id,
            AUTHENTICATE.id,
        ):
            return

        definition = self.message_registry.get(
            packet.message_type,
        )

        if definition is None:
            return

        if definition is not WATCH_PEERS:
            return

        payload = self.pipeline.receive(
            definition,
            packet.payload,
        )

        await self.handle_watch_peers(
            sender=sender,
            peers=payload,
        )

    async def handle_watch_peers(
        self,
        sender: Peer,
        peers: list[bytes],
    ) -> None:
        self.peer_watch_manager.set_following(
            follower=sender.public_key,
            targets=set(peers),
        )

        online_peers = [target for target in peers if self.peer_manager.get(target) is not None]

        response_payload = self.pipeline.send(
            WATCH_PEERS,
            online_peers,
        )

        response_packet = Packet(
            peer=RESERVED_KEY,
            message_type=WATCH_PEERS.id,
            payload=response_payload,
        )

        await sender.send(
            response_packet.encode(),
        )

    async def send_peer_status(
        self,
        peer: Peer,
        target: bytes,
        is_online: bool,
    ) -> None:
        definition = PEER_ONLINE if is_online else PEER_OFFLINE

        payload = self.pipeline.send(
            definition,
            target,
        )

        packet = Packet(
            peer=RESERVED_KEY,
            message_type=definition.id,
            payload=payload,
        )

        await peer.send(
            packet.encode(),
        )
