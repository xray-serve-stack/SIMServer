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


# Android SMS record type values, kept numeric on the wire.
# 1 = INBOX, 2 = SENT, 3 = DRAFT, 4 = OUTBOX, 5 = FAILED, 6 = QUEUED
MESSAGE_TYPE_MIN = 1
MESSAGE_TYPE_MAX = 6


class GetMessagesPayloadCodec(PayloadCodec[dict[str, object]]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> dict[str, object]:
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidPayload("Invalid GET_MESSAGES payload") from exc

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
                GetMessagesPayloadCodec._validate_response(data)
            case PeerRole.SERVE:
                GetMessagesPayloadCodec._validate_request(data)
            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

    @staticmethod
    def serialize_data(
        peer_role: PeerRole,
        data: object,
    ) -> None:
        match peer_role:
            case PeerRole.CLIENT:
                GetMessagesPayloadCodec._validate_request(data)
            case PeerRole.SERVE:
                GetMessagesPayloadCodec._validate_response(data)
            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

    @staticmethod
    def _validate_request(data: object) -> None:
        if not isinstance(data, dict):
            raise InvalidPayload("GET_MESSAGES request data must be an object")

        subscription_ids = data.get("subscription_ids")

        if not isinstance(subscription_ids, list) or not subscription_ids:
            raise InvalidPayload("GET_MESSAGES subscription_ids must be a non-empty array")

        if any(
            not isinstance(subscription_id, int) or isinstance(subscription_id, bool)
            for subscription_id in subscription_ids
        ):
            raise InvalidPayload("GET_MESSAGES subscription_ids must contain only integers")

        number = data.get("number")

        if not isinstance(number, str) or len(number) < 1:
            raise InvalidPayload("GET_MESSAGES number must be a non-empty string")

        for field in ("start", "end"):
            value = data.get(field)

            if value is not None and (not isinstance(value, int) or isinstance(value, bool)):
                raise InvalidPayload(f"GET_MESSAGES {field} must be an integer or null")

        start = data.get("start")
        end = data.get("end")

        if start is not None and end is not None and start > end:
            raise InvalidPayload("GET_MESSAGES start must be less than or equal to end")

        cached_count = data.get("cached_count")

        if cached_count is not None and (
            not isinstance(cached_count, int) or isinstance(cached_count, bool) or cached_count < 0
        ):
            raise InvalidPayload("GET_MESSAGES cached_count must be a non-negative integer or null")

        limit = data.get("limit")

        if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool) or limit <= 0):
            raise InvalidPayload("GET_MESSAGES limit must be a positive integer or null")

    @staticmethod
    def _validate_response(data: object) -> None:
        if not isinstance(data, dict):
            raise InvalidPayload("GET_MESSAGES response data must be an object")

        messages = data.get("messages")

        if not isinstance(messages, list):
            raise InvalidPayload("GET_MESSAGES messages must be an array")

        for message in messages:
            GetMessagesPayloadCodec._validate_message(message)  # type: ignore

        remaining = data.get("remaining")

        if not isinstance(remaining, int) or isinstance(remaining, bool) or remaining < 0:
            raise InvalidPayload("GET_MESSAGES remaining must be a non-negative integer")

        next_start = data.get("next_start")

        if next_start is not None and (
            not isinstance(next_start, int) or isinstance(next_start, bool) or next_start < 0
        ):
            raise InvalidPayload("GET_MESSAGES next_start must be a non-negative integer or null")

    @staticmethod
    def _validate_message(message: object) -> None:
        if not isinstance(message, dict):
            raise InvalidPayload("GET_MESSAGES message must be an object")

        body = message.get("body")

        if not isinstance(body, str):
            raise InvalidPayload("GET_MESSAGES message body must be a string")

        timestamp = message.get("timestamp")

        if not isinstance(timestamp, int) or isinstance(timestamp, bool) or timestamp < 0:
            raise InvalidPayload("GET_MESSAGES message timestamp must be a non-negative integer")

        subscription_id = message.get("subscription_id")

        if not isinstance(subscription_id, int) or isinstance(subscription_id, bool):
            raise InvalidPayload("GET_MESSAGES message subscription_id must be an integer")

        message_type = message.get("type")

        if not isinstance(message_type, int) or isinstance(message_type, bool):
            raise InvalidPayload("GET_MESSAGES message type must be an integer")

        if not (MESSAGE_TYPE_MIN <= message_type <= MESSAGE_TYPE_MAX):
            raise InvalidPayload(
                f"GET_MESSAGES message type must be in range {MESSAGE_TYPE_MIN}..{MESSAGE_TYPE_MAX}"
            )


GET_MESSAGES = MessageDefinition(
    id=13,
    name="GET_MESSAGES",
    kind=MessageKind.COMMAND,
    category=MessageCategory.SMS,
    expire_after=None,
    outcomes=(),
    description="Request SMS messages from the Serve.",
    payload_protection=PayloadProtection.ENCRYPTED,
    payload_codec=GetMessagesPayloadCodec(),
)
