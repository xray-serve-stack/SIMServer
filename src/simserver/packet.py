from dataclasses import dataclass

from .message_definitions.REGISTER import PUBLIC_KEY_SIZE


MESSAGE_TYPE_SIZE = 8
HEADER_SIZE = PUBLIC_KEY_SIZE + MESSAGE_TYPE_SIZE


@dataclass(frozen=True, slots=True)
class Packet:
    peer: bytes
    message_type: int
    payload: bytes

    def encode(self) -> bytes:
        if len(self.peer) != PUBLIC_KEY_SIZE:
            raise ValueError("Peer public key must be exactly 32 bytes")

        if not 0 <= self.message_type <= 0xFFFFFFFFFFFFFFFF:
            raise ValueError("Message type must fit uint64")

        return (
            self.peer
            + self.message_type.to_bytes(
                MESSAGE_TYPE_SIZE,
                "big",
            )
            + self.payload
        )

    @classmethod
    def decode(cls, data: bytes) -> "Packet":
        if len(data) < HEADER_SIZE:
            raise ValueError("Packet too short")

        peer = data[:PUBLIC_KEY_SIZE]

        message_type = int.from_bytes(
            data[PUBLIC_KEY_SIZE:HEADER_SIZE],
            "big",
        )

        payload = data[HEADER_SIZE:]

        return cls(
            peer=peer,
            message_type=message_type,
            payload=payload,
        )
