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


class PeerOnlinePayloadCodec(PayloadCodec[bytes]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> bytes:
        if peer_role is not PeerRole.CLIENT:
            raise InvalidPayload("PEER_ONLINE can only be received by CLIENT")

        if len(payload) != PUBLIC_KEY_SIZE:
            raise InvalidPayload("PEER_ONLINE payload must be exactly 32 bytes")

        return payload

    def serialize(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> bytes:
        if peer_role is not PeerRole.SERVER:
            raise InvalidPayload("PEER_ONLINE can only be sent by SERVER")

        if len(payload) != PUBLIC_KEY_SIZE:
            raise InvalidPayload("PEER_ONLINE payload must be exactly 32 bytes")

        return payload


PEER_ONLINE = MessageDefinition(
    id=3,
    name="PEER_ONLINE",
    kind=MessageKind.EVENT,
    category=MessageCategory.SYSTEM,
    expire_after=None,
    outcomes=(),
    description="Notify a peer that another peer is online.",
    payload_protection=PayloadProtection.PLAINTEXT,
    payload_codec=PeerOnlinePayloadCodec(),
)
