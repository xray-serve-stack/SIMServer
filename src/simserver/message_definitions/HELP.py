import json

from ..protocol import (
    PayloadProtection,
    PeerRole,
    MessageKind,
    MessageCategory,
    InvalidPayload,
    PayloadCodec,
    MessageDefinition,
)
from .VALIDATE_COMMANDS import validate_command


class HelpPayloadCodec(PayloadCodec[dict[str, object]]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> dict[str, object]:
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidPayload("Invalid HELP payload") from exc

        command = validate_command(parsed)
        data = command["data"]

        match peer_role:
            case PeerRole.CLIENT:
                if not isinstance(data, dict) or data:
                    raise InvalidPayload("HELP request data must be an empty object")

            case PeerRole.SERVE:
                if not isinstance(data, str):
                    raise InvalidPayload("HELP response data must be a string")

            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

        return command

    def serialize(
        self,
        peer_role: PeerRole,
        payload: dict[str, object],
    ) -> bytes:
        validate_command(payload)
        data = payload["data"]

        match peer_role:
            case PeerRole.CLIENT:
                if not isinstance(data, dict) or data:
                    raise InvalidPayload("HELP request data must be an empty object")

            case PeerRole.SERVE:
                if not isinstance(data, str):
                    raise InvalidPayload("HELP response data must be a string")

            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

        return json.dumps(payload).encode("utf-8")


HELP = MessageDefinition(
    id=10,
    name="HELP",
    kind=MessageKind.COMMAND,
    category=MessageCategory.SYSTEM,
    expire_after=None,
    outcomes=(),
    description="Request help information from the Serve.",
    payload_protection=PayloadProtection.ENCRYPTED,
    payload_codec=HelpPayloadCodec(),
)
