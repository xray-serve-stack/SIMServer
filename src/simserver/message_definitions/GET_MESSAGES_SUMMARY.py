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


class MessagesSummaryPayloadCodec(PayloadCodec[dict[str, object]]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> dict[str, object]:
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidPayload("Invalid GET_MESSAGES_SUMMARY payload") from exc

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
                MessagesSummaryPayloadCodec._validate_response(data)
            case PeerRole.SERVE:
                MessagesSummaryPayloadCodec._validate_request(data)
            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

    @staticmethod
    def serialize_data(
        peer_role: PeerRole,
        data: object,
    ) -> None:
        match peer_role:
            case PeerRole.CLIENT:
                MessagesSummaryPayloadCodec._validate_request(data)
            case PeerRole.SERVE:
                MessagesSummaryPayloadCodec._validate_response(data)
            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

    @staticmethod
    def _validate_request(data: object) -> None:
        if not isinstance(data, dict):
            raise InvalidPayload("GET_MESSAGES_SUMMARY request data must be an object")

        subscription_ids = data.get("subscription_ids")

        if not isinstance(subscription_ids, list) or not subscription_ids:
            raise InvalidPayload("GET_MESSAGES_SUMMARY subscription_ids must be a non-empty array")

        if any(
            not isinstance(subscription_id, int) or isinstance(subscription_id, bool)
            for subscription_id in subscription_ids
        ):
            raise InvalidPayload("GET_MESSAGES_SUMMARY subscription_ids must contain only integers")

    @staticmethod
    def _validate_response(data: object) -> None:
        if not isinstance(data, dict):
            raise InvalidPayload("GET_MESSAGES_SUMMARY response data must be an object")

        subscription_ids = data.get("subscription_ids")

        if not isinstance(subscription_ids, list) or not subscription_ids:
            raise InvalidPayload("GET_MESSAGES_SUMMARY response subscription_ids must be a non-empty array")

        if any(
            not isinstance(subscription_id, int) or isinstance(subscription_id, bool)
            for subscription_id in subscription_ids
        ):
            raise InvalidPayload("GET_MESSAGES_SUMMARY response subscription_ids must contain only integers")

        conversations = data.get("conversations")

        if not isinstance(conversations, list):
            raise InvalidPayload("GET_MESSAGES_SUMMARY response conversations must be an array")

        for conversation in conversations:
            MessagesSummaryPayloadCodec._validate_conversation(conversation)  # type: ignore

    @staticmethod
    def _validate_conversation(conversation: object) -> None:
        if not isinstance(conversation, dict):
            raise InvalidPayload("GET_MESSAGES_SUMMARY conversation must be an object")

        number = conversation.get("number")

        if not isinstance(number, str) or len(number) < 1:
            raise InvalidPayload("GET_MESSAGES_SUMMARY conversation number must be a non-empty string")

        message_count = conversation.get("message_count")

        if not isinstance(message_count, int) or isinstance(message_count, bool) or message_count < 0:
            raise InvalidPayload(
                "GET_MESSAGES_SUMMARY conversation message_count must be a non-negative integer"
            )

        unread_count = conversation.get("unread_count")

        if not isinstance(unread_count, int) or isinstance(unread_count, bool) or unread_count < 0:
            raise InvalidPayload(
                "GET_MESSAGES_SUMMARY conversation unread_count must be a non-negative integer"
            )

        last_message = conversation.get("last_message")

        if not isinstance(last_message, int) or isinstance(last_message, bool) or last_message < 0:
            raise InvalidPayload(
                "GET_MESSAGES_SUMMARY conversation last_message must be a non-negative integer"
            )


GET_MESSAGES_SUMMARY = MessageDefinition(
    id=14,
    name="GET_MESSAGES_SUMMARY",
    kind=MessageKind.COMMAND,
    category=MessageCategory.SMS,
    expire_after=None,
    outcomes=(),
    description="Request a summary of SMS messages from the Serve.",
    payload_protection=PayloadProtection.ENCRYPTED,
    payload_codec=MessagesSummaryPayloadCodec(),
)
