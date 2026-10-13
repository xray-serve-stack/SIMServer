from ..protocol import (
    PayloadProtection,
    PeerRole,
    MessageKind,
    MessageCategory,
    InvalidPayload,
    PayloadCodec,
    MessageDefinition,
)


NONCE_SIZE = 32


class AuthenticatePayloadCodec(PayloadCodec[dict[str, object]]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> dict[str, object]:
        if peer_role not in (
            PeerRole.SERVER,
            PeerRole.CLIENT,
            PeerRole.SERVE,
        ):
            raise InvalidPayload(f"Unsupported peer role: {peer_role}")

        if len(payload) != NONCE_SIZE:
            raise InvalidPayload("AUTHENTICATE payload must be exactly 32 bytes")

        return {
            "nonce": payload,
        }

    def serialize(
        self,
        peer_role: PeerRole,
        payload: dict[str, object],
    ) -> bytes:
        if peer_role not in (
            PeerRole.SERVER,
            PeerRole.CLIENT,
            PeerRole.SERVE,
        ):
            raise InvalidPayload(f"Unsupported peer role: {peer_role}")

        nonce = payload.get("nonce")

        if not isinstance(nonce, bytes):
            raise InvalidPayload("AUTHENTICATE nonce must be bytes")

        if len(nonce) != NONCE_SIZE:
            raise InvalidPayload("AUTHENTICATE nonce must be exactly 32 bytes")

        return nonce


AUTHENTICATE = MessageDefinition(
    id=1,
    name="AUTHENTICATE",
    kind=MessageKind.PROTOCOL,
    category=MessageCategory.SYSTEM,
    expire_after=None,
    outcomes=(),
    description="Authenticate a peer using a challenge nonce.",
    payload_protection=PayloadProtection.ENCRYPTED,
    payload_codec=AuthenticatePayloadCodec(),
)
