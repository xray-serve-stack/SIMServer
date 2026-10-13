from typing import Any
from .protocol import MessageKind, MessageDefinition


class MessageRegistry:
    def __init__(
        self,
        definitions: tuple[MessageDefinition[Any], ...],
    ) -> None:
        self._by_id = {definition.id: definition for definition in definitions}

        self._by_name = {definition.name: definition for definition in definitions}

    def get(self, message_id: int) -> MessageDefinition[Any] | None:
        return self._by_id.get(message_id)

    def get_by_name(self, name: str) -> MessageDefinition[Any] | None:
        return self._by_name.get(name)

    def all(self) -> tuple[MessageDefinition[Any], ...]:
        return tuple(self._by_id.values())

    def commands(self) -> tuple[MessageDefinition[Any], ...]:
        return tuple(
            definition for definition in self._by_id.values() if definition.kind is MessageKind.COMMAND
        )

    def events(self) -> tuple[MessageDefinition[Any], ...]:
        return tuple(definition for definition in self._by_id.values() if definition.kind is MessageKind.EVENT)

    def protocol(self) -> tuple[MessageDefinition[Any], ...]:
        return tuple(
            definition for definition in self._by_id.values() if definition.kind is MessageKind.PROTOCOL
        )
