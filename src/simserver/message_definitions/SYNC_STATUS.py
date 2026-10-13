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
from .GET_SIMS import GetSimsPayloadCodec
from .GET_CONVERSATIONS import GetConversationsPayloadCodec
from .GET_MESSAGES_SUMMARY import MessagesSummaryPayloadCodec


RESPONSE_KEYS = (
    "GET_SIMS",
    "GET_CONVERSATIONS",
    "GET_MESSAGES_SUMMARY",
)


class SyncStatusPayloadCodec(PayloadCodec[dict[str, object]]):
    """
    Composite SYNC_STATUS command codec.

    Direction model (peer_role identifies the acting peer):

        CLIENT + send    -> serialize request   (data == {})
        SERVE  + receive -> parse request       (data == {})
        SERVE  + send    -> serialize response  (3 nested results)
        CLIENT + receive -> parse response      (3 nested results)

    parse()/serialize() only handle the COMMAND envelope and JSON
    encoding/decoding. All data-level validation is delegated to
    parse_data()/serialize_data(), which in turn delegate to the
    primitive codecs' parse_data()/serialize_data().
    """

    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> dict[str, object]:
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidPayload("Invalid SYNC_STATUS payload") from exc

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
                # CLIENT is receiving a response.
                SyncStatusPayloadCodec._validate_response_structure(data)
                GetSimsPayloadCodec().parse_data(PeerRole.CLIENT, data["GET_SIMS"])  # type: ignore
                GetConversationsPayloadCodec().parse_data(PeerRole.CLIENT, data["GET_CONVERSATIONS"])  # type: ignore
                MessagesSummaryPayloadCodec().parse_data(PeerRole.CLIENT, data["GET_MESSAGES_SUMMARY"])  # type: ignore

            case PeerRole.SERVE:
                # SERVE is receiving a request.
                SyncStatusPayloadCodec._validate_request(data)

            case _:
                raise InvalidPayload(f"SYNC_STATUS is not supported for peer role: {peer_role}")

    @staticmethod
    def serialize_data(
        peer_role: PeerRole,
        data: object,
    ) -> None:
        match peer_role:
            case PeerRole.CLIENT:
                # CLIENT is sending a request.
                SyncStatusPayloadCodec._validate_request(data)

            case PeerRole.SERVE:
                # SERVE is sending a response.
                SyncStatusPayloadCodec._validate_response_structure(data)
                GetSimsPayloadCodec().serialize_data(PeerRole.SERVE, data["GET_SIMS"])  # type: ignore
                GetConversationsPayloadCodec().serialize_data(PeerRole.SERVE, data["GET_CONVERSATIONS"])  # type: ignore
                MessagesSummaryPayloadCodec().serialize_data(PeerRole.SERVE, data["GET_MESSAGES_SUMMARY"])  # type: ignore

            case _:
                raise InvalidPayload(f"SYNC_STATUS is not supported for peer role: {peer_role}")

    @staticmethod
    def _validate_request(data: object) -> None:
        if not isinstance(data, dict):
            raise InvalidPayload("SYNC_STATUS request data must be an object")

        if data:
            raise InvalidPayload("SYNC_STATUS request data must be empty")

    @staticmethod
    def _validate_response_structure(data: object) -> None:
        if not isinstance(data, dict):
            raise InvalidPayload("SYNC_STATUS response data must be an object")

        for key in RESPONSE_KEYS:
            if key not in data:
                raise InvalidPayload(f"SYNC_STATUS response is missing '{key}'")


SYNC_STATUS = MessageDefinition(
    id=1000,
    name="SYNC_STATUS",
    kind=MessageKind.COMMAND,
    category=MessageCategory.SYSTEM,
    expire_after=None,
    outcomes=(),
    description="Composite command that returns SIMs, conversations and message summaries in one response.",
    payload_protection=PayloadProtection.ENCRYPTED,
    payload_codec=SyncStatusPayloadCodec(),
)
