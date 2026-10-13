from ..protocol import InvalidPayload


def validate_command(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise InvalidPayload("Command payload must be a JSON object")

    required_keys = {
        "request_id",
        "created_at",
        "process_at",
        "data",
    }

    missing_keys = required_keys - payload.keys()
    if missing_keys:
        raise InvalidPayload(f"Command payload is missing required keys: {missing_keys}")

    if not isinstance(payload["request_id"], int):
        raise InvalidPayload("request_id must be an integer")

    if not isinstance(payload["created_at"], int):
        raise InvalidPayload("created_at must be an integer")

    if not isinstance(payload["process_at"], int):
        raise InvalidPayload("process_at must be an integer")

    return payload
