from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Generic, TypeVar


T = TypeVar("T")


class PayloadProtection(Enum):
    PLAINTEXT = auto()
    ENCRYPTED = auto()


class PeerRole(Enum):
    SERVER = "server"
    CLIENT = "client"
    SERVE = "serve"


class MessageKind(str, Enum):
    COMMAND = "command"
    EVENT = "event"
    PROTOCOL = "protocol"


class MessageCategory(str, Enum):
    SYSTEM = "system"
    SMS = "sms"
    SIM = "sim"
    CONVERSATION = "conversation"


class ProtocolError(Exception):
    pass


class InvalidPayload(ProtocolError):
    pass


class PayloadCodec(Generic[T], ABC):
    @abstractmethod
    def parse(self, peer_role: PeerRole, payload: bytes) -> T: ...

    @abstractmethod
    def serialize(self, peer_role: PeerRole, payload: T) -> bytes: ...


@dataclass(frozen=True, slots=True)
class MessageDefinition(Generic[T]):
    id: int
    name: str
    kind: MessageKind
    category: MessageCategory
    expire_after: int | None
    outcomes: tuple[int, ...]
    description: str
    payload_protection: PayloadProtection
    payload_codec: PayloadCodec[T]

    help: str | None = None
