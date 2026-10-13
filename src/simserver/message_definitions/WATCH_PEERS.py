from ..protocol import (
    PayloadProtection,
    PeerRole,
    MessageKind,
    MessageCategory,
    InvalidPayload,
    PayloadCodec,
    MessageDefinition,
)
from .REGISTER import PUBLIC_KEY_SIZE


class WatchPeersPayloadCodec(PayloadCodec[list[bytes]]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> list[bytes]:
        if peer_role not in (
            PeerRole.SERVER,
            PeerRole.CLIENT,
        ):
            raise InvalidPayload("WATCH_PEERS is not valid for SERVE")

        if len(payload) == 0 or len(payload) % PUBLIC_KEY_SIZE != 0:
            raise InvalidPayload("WATCH_PEERS payload must contain 32-byte public keys")

        return [
            payload[i : i + PUBLIC_KEY_SIZE]
            for i in range(
                0,
                len(payload),
                PUBLIC_KEY_SIZE,
            )
        ]

    def serialize(
        self,
        peer_role: PeerRole,
        payload: list[bytes],
    ) -> bytes:
        if peer_role not in (
            PeerRole.CLIENT,
            PeerRole.SERVER,
        ):
            raise InvalidPayload("WATCH_PEERS is not valid for SERVE")

        for public_key in payload:
            if len(public_key) != PUBLIC_KEY_SIZE:
                raise InvalidPayload("WATCH_PEERS public keys must be exactly 32 bytes")

        return b"".join(payload)


WATCH_PEERS = MessageDefinition(
    id=2,
    name="WATCH_PEERS",
    kind=MessageKind.PROTOCOL,
    category=MessageCategory.SYSTEM,
    expire_after=None,
    outcomes=(),
    description="Request online notifications for selected peers.",
    payload_protection=PayloadProtection.PLAINTEXT,
    payload_codec=WatchPeersPayloadCodec(),
)
