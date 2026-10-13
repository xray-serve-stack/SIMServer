from typing import Callable
from .protocol import (
    T,
    PayloadProtection,
    PeerRole,
    ProtocolError,
    MessageDefinition,
)


class PayloadPipeline:
    def __init__(self, peer_role: PeerRole) -> None:
        self._peer_role = peer_role
        self._encrypt: Callable[[bytes], bytes] | None = None
        self._decrypt: Callable[[bytes], bytes] | None = None

    def set_encryption(
        self,
        encrypt: Callable[[bytes], bytes],
        decrypt: Callable[[bytes], bytes],
    ) -> None:
        self._encrypt = encrypt
        self._decrypt = decrypt

    def send(
        self,
        definition: MessageDefinition[T],
        payload: T,
    ) -> bytes:
        payload_bytes = definition.payload_codec.serialize(self._peer_role, payload)

        match definition.payload_protection:
            case PayloadProtection.PLAINTEXT:
                return payload_bytes

            case PayloadProtection.ENCRYPTED:
                if self._encrypt is None:
                    raise ProtocolError("Encryption is not configured")

                return self._encrypt(payload_bytes)

            case _:
                raise ProtocolError(f"Unsupported payload protection: {definition.payload_protection}")

    def receive(
        self,
        definition: MessageDefinition[T],
        payload: bytes,
    ) -> T:
        match definition.payload_protection:
            case PayloadProtection.PLAINTEXT:
                return definition.payload_codec.parse(self._peer_role, payload)

            case PayloadProtection.ENCRYPTED:
                if self._decrypt is None:
                    raise ProtocolError("Decryption is not configured")

                return definition.payload_codec.parse(
                    self._peer_role,
                    self._decrypt(payload),
                )

            case _:
                raise ProtocolError(f"Unsupported payload protection: {definition.payload_protection}")
