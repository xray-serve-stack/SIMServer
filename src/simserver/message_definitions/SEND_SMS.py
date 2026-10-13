import json

from ..protocol import (
    InvalidPayload,
    MessageCategory,
    MessageDefinition,
    MessageKind,
    PeerRole,
    PayloadCodec,
    PayloadProtection,
)
from .VALIDATE_COMMANDS import validate_command


class SendSmsPayloadCodec(PayloadCodec[dict[str, object]]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> dict[str, object]:
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidPayload("Invalid SEND_SMS payload") from exc

        command = validate_command(parsed)
        self.parse_data(peer_role, command["data"])

        return command

    def serialize(
        self,
        peer_role: PeerRole,
        payload: dict[str, object],
    ) -> bytes:
        command = validate_command(payload)
        self.serialize_data(peer_role, command["data"])

        return json.dumps(command).encode("utf-8")

    @staticmethod
    def parse_data(
        peer_role: PeerRole,
        data: object,
    ) -> None:
        match peer_role:
            case PeerRole.CLIENT:
                SendSmsPayloadCodec._validate_response(data)
            case PeerRole.SERVE:
                SendSmsPayloadCodec._validate_request(data)
            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

    @staticmethod
    def serialize_data(
        peer_role: PeerRole,
        data: object,
    ) -> None:
        match peer_role:
            case PeerRole.CLIENT:
                SendSmsPayloadCodec._validate_request(data)
            case PeerRole.SERVE:
                SendSmsPayloadCodec._validate_response(data)
            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

    @staticmethod
    def _validate_request(data: object) -> None:
        if not isinstance(data, dict):
            raise InvalidPayload("SEND_SMS request data must be an object")

        subscription_id = data.get("subscription_id")
        if not isinstance(subscription_id, int) or isinstance(subscription_id, bool):
            raise InvalidPayload("SEND_SMS subscription_id must be an integer")

        number = data.get("number")
        if not isinstance(number, str) or not number:
            raise InvalidPayload("SEND_SMS number must be a non-empty string")

        body = data.get("body")
        if not isinstance(body, str) or not body:
            raise InvalidPayload("SEND_SMS body must be a non-empty string")

    @staticmethod
    def _validate_response(data: object) -> None:
        if not isinstance(data, dict):
            raise InvalidPayload("SEND_SMS response data must be an object")

        accepted = data.get("accepted")
        if not isinstance(accepted, bool):
            raise InvalidPayload("SEND_SMS response accepted must be a boolean")

        if accepted is False:
            reason = data.get("reason")
            if not isinstance(reason, str):
                raise InvalidPayload("SEND_SMS response reason must be a string when accepted is false")


SEND_SMS = MessageDefinition(
    id=15,
    name="SEND_SMS",
    kind=MessageKind.COMMAND,
    category=MessageCategory.SMS,
    expire_after=None,
    outcomes=(),
    description="Send a single-part SMS message from the Serve.",
    payload_protection=PayloadProtection.ENCRYPTED,
    payload_codec=SendSmsPayloadCodec(),
)
