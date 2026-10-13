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


SIM_FIELDS = {
    "subscription_id",
    "slot_index",
    "number",
    "carrier_name",
    "display_name",
    "country_iso",
    "mcc",
    "mnc",
    "is_default_sms",
}


class GetSimsPayloadCodec(PayloadCodec[dict[str, object]]):
    def parse(
        self,
        peer_role: PeerRole,
        payload: bytes,
    ) -> dict[str, object]:
        try:
            parsed = json.loads(payload)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise InvalidPayload("Invalid GET_SIMS payload") from exc

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
                GetSimsPayloadCodec._validate_response(data)
            case PeerRole.SERVE:
                GetSimsPayloadCodec._validate_request(data)
            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

    @staticmethod
    def serialize_data(
        peer_role: PeerRole,
        data: object,
    ) -> None:
        match peer_role:
            case PeerRole.CLIENT:
                GetSimsPayloadCodec._validate_request(data)
            case PeerRole.SERVE:
                GetSimsPayloadCodec._validate_response(data)
            case _:
                raise InvalidPayload(f"Unsupported peer role: {peer_role}")

    @staticmethod
    def _validate_request(data: object) -> None:
        if not isinstance(data, dict) or data:
            raise InvalidPayload("GET_SIMS request data must be an empty object")

    @staticmethod
    def _validate_response(data: object) -> None:
        if not isinstance(data, list):
            raise InvalidPayload("GET_SIMS response data must be an array")

        for sim in data:
            if not isinstance(sim, dict):
                raise InvalidPayload("GET_SIMS response must contain SIM objects")

            missing_fields = SIM_FIELDS - sim.keys()
            if missing_fields:
                raise InvalidPayload(f"GET_SIMS SIM object is missing fields: {missing_fields}")

            if not isinstance(sim["subscription_id"], int) or isinstance(sim["subscription_id"], bool):
                raise InvalidPayload("GET_SIMS subscription_id must be an integer")


GET_SIMS = MessageDefinition(
    id=11,
    name="GET_SIMS",
    kind=MessageKind.COMMAND,
    category=MessageCategory.SIM,
    expire_after=None,
    outcomes=(),
    description="Request the active SIM subscriptions from the Serve.",
    payload_protection=PayloadProtection.ENCRYPTED,
    payload_codec=GetSimsPayloadCodec(),
)
