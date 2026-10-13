from ..protocol import (
    PayloadProtection,
    PeerRole,
    MessageKind,
    MessageCategory,
    InvalidPayload,
    PayloadCodec,
    MessageDefinition,
)


PUBLIC_KEY_SIZE = 32


class RegisterPayloadCodec(PayloadCodec[dict[str, object]]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> dict[str, object]:
        """
        REGISTER packet contract:

        Wire header:
            peer        = ZERO (32 bytes)
            message_type = REGISTER (8 bytes)

        Payload:
            public_key = 32-byte public key

        The ZERO peer requirement belongs to packet/protocol validation,
        because PayloadCodec only receives peer_role and payload.
        """
        if peer_role is not PeerRole.SERVER:
            raise InvalidPayload("REGISTER can only be received by SERVER")

        if len(payload) != PUBLIC_KEY_SIZE:
            raise InvalidPayload("REGISTER payload must be exactly 32 bytes")

        return {
            "public_key": payload,
        }

    def serialize(
        self,
        peer_role: PeerRole,
        payload: dict[str, object],
    ) -> bytes:
        """
        REGISTER packet contract:

        Wire header:
            peer         = ZERO (32 bytes)
            message_type = REGISTER (8 bytes)

        Payload:
            public_key = 32-byte public key

        The ZERO peer requirement belongs to packet/protocol validation,
        because PayloadCodec only receives peer_role and payload.
        """
        if peer_role not in (
            PeerRole.CLIENT,
            PeerRole.SERVE,
        ):
            raise InvalidPayload("REGISTER can only be sent by CLIENT or SERVE")

        public_key = payload.get("public_key")

        if not isinstance(public_key, bytes):
            raise InvalidPayload("REGISTER public_key must be bytes")

        if len(public_key) != PUBLIC_KEY_SIZE:
            raise InvalidPayload("REGISTER public_key must be exactly 32 bytes")

        return public_key


REGISTER = MessageDefinition(
    id=0,
    name="REGISTER",
    kind=MessageKind.PROTOCOL,
    category=MessageCategory.SYSTEM,
    expire_after=None,
    outcomes=(),
    description="Register a peer public key with the server.",
    payload_protection=PayloadProtection.PLAINTEXT,
    payload_codec=RegisterPayloadCodec(),
)
