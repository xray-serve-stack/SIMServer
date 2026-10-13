# SIMServe Protocol

**Current version:** `v1`

This document defines the communication contract between SIMServer and SIMServe.

The protocol is intentionally small at the current development stage.

---

# 1. Overview

SIMServer and SIMServe communicate over a persistent WebSocket connection.

The current protocol contains two categories of messages:

### Connection-level

```text
register
registered
```

### Command-level

```text
command
result
```

The basic flow is:

```text
SIMServe                         SIMServer
   │                                │
   │──── register ─────────────────►│
   │                                │
   │◄─── registered ────────────────│
   │                                │
   │◄─── command ───────────────────│
   │                                │
   │──── result ───────────────────►│
   │                                │
```

---

# 2. Registration

Registration identifies a new Server-side Serve connection.

## 2.1 Serve → Server

SIMServe sends:

```json
{
  "type": "register"
}
```

No additional fields are currently required.

---

## 2.2 Server → Serve

SIMServer responds:

```json
{
  "type": "registered",
  "serve_id": "serve-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

The Server generates `serve_id`.

### Current behavior

The current implementation associates `serve_id` with the active connection.

### Planned behavior

In a future protocol revision, the Serve will retain a persistent identity across reconnects.

This is not implemented in Protocol v1.

---

# 3. Command

A Command is sent from SIMServer to SIMServe.

## 3.1 Structure

```json
{
  "type": "command",
  "request_id": "unique-request-id",
  "command": "command-name",
  "created_at": "yyyyMMddHHmmss",
  "data": {}
}
```

### Fields

| Field        | Type   | Required | Description                            |
| ------------ | ------ | -------- | -------------------------------------- |
| `type`       | string | yes      | Must be `command`                      |
| `request_id` | string | yes      | Correlates the command with its result |
| `command`    | string | yes      | Name of the command                    |
| `created_at` | string | yes      | Command creation timestamp             |
| `data`       | object | yes      | Command-specific parameters            |

---

# 4. Result

A Result is sent from SIMServe to SIMServer after command execution.

## 4.1 Structure

```json
{
  "type": "result",
  "request_id": "unique-request-id",
  "command": "command-name",
  "created_at": "yyyyMMddHHmmss",
  "processed_at": "yyyyMMddHHmmss",
  "success": true,
  "data": {},
  "error": null
}
```

### Fields

| Field          | Type        | Required | Description                         |
| -------------- | ----------- | -------- | ----------------------------------- |
| `type`         | string      | yes      | Must be `result`                    |
| `request_id`   | string      | yes      | Must match the original Command     |
| `command`      | string      | yes      | Command that produced the result    |
| `created_at`   | string      | yes      | Original command creation timestamp |
| `processed_at` | string      | yes      | Time command processing completed   |
| `success`      | boolean     | yes      | Whether execution succeeded         |
| `data`         | any         | yes      | Command result data or `null`       |
| `error`        | string/null | yes      | Error description or `null`         |

---

# 5. Request Correlation

`request_id` is the primary correlation key.

Example:

```text
Command
request_id = abc-001

        ↓

Result
request_id = abc-001
```

SIMServer uses this identifier to associate an incoming Result with the pending command request.

Two commands may be active simultaneously as long as their `request_id` values are different.

---

# 6. Server Routing

`serve_id` is a Server-side routing concept.

It is not included in the WebSocket Command message.

For example, the Server HTTP command interface may receive:

```json
{
  "serve_id": "serve-123",
  "request_id": "req-001",
  "command": "summary",
  "created_at": "20260911122000",
  "data": {
    "sim": 0
  }
}
```

SIMServer uses `serve_id` to select the appropriate WebSocket connection.

The message sent to SIMServe is:

```json
{
  "type": "command",
  "request_id": "req-001",
  "command": "summary",
  "created_at": "20260911122000",
  "data": {
    "sim": 0
  }
}
```

Therefore:

```text
serve_id
   │
   │ Server routing only
   ▼
ServeConnection
   │
   ▼
WebSocket
   │
   ▼
Command
```

---

# 7. Command: `summary`

Returns an SMS conversation summary for a selected SIM.

## Request

```json
{
  "type": "command",
  "request_id": "summary-001",
  "command": "summary",
  "created_at": "20260911122000",
  "data": {
    "sim": 0
  }
}
```

## Parameters

| Field | Type    | Required | Description    |
| ----- | ------- | -------- | -------------- |
| `sim` | integer | yes      | SIM slot index |

Current SIM slot convention:

```text
SIM 1 → 0
SIM 2 → 1
```

## Successful Result

Example:

```json
{
  "type": "result",
  "request_id": "summary-001",
  "command": "summary",
  "created_at": "20260911122000",
  "processed_at": "20260911122001",
  "success": true,
  "data": [
    {
      "number": "+49123456789",
      "message_count": 4,
      "last_message": "2026-09-11 12:15:00",
      "preview": "Example message"
    }
  ],
  "error": null
}
```

The exact data returned is determined by the current SIMServe implementation.

---

# 8. Command: `history`

Returns SMS history for a selected SIM and number.

## Request

```json
{
  "type": "command",
  "request_id": "history-001",
  "command": "history",
  "created_at": "20260911122000",
  "data": {
    "sim": 0,
    "number": "+49123456789",
    "start": "2026-01-01 00:00:00",
    "end": "2026-01-02 00:00:00"
  }
}
```

## Parameters

| Field    | Type    | Required                 | Description        |
| -------- | ------- | ------------------------ | ------------------ |
| `sim`    | integer | yes                      | SIM slot index     |
| `number` | string  | yes                      | SMS address/number |
| `start`  | string  | implementation-dependent | Start time         |
| `end`    | string  | implementation-dependent | End time           |

Timestamp format for history filters:

```text
yyyy-MM-dd HH:mm:ss
```

The current implementation supports explicit start/end values.

Optional/no-date semantics are planned for refinement and should not be assumed to be finalized in Protocol v1.

---

# 9. Errors

A failed command returns:

```json
{
  "type": "result",
  "request_id": "history-001",
  "command": "history",
  "created_at": "20260911122000",
  "processed_at": "20260911122001",
  "success": false,
  "data": null,
  "error": "Missing sim"
}
```

The `error` field contains a human-readable description.

---

# 10. Unknown Commands

If SIMServe receives an unknown command, it returns a Result with:

```json
{
  "success": false,
  "error": "Unknown command"
}
```

The original:

```text
request_id
command
created_at
```

must remain associated with the Result.

---

# 11. Protocol Boundaries

The following distinction is important:

```text
Registration
    ↓
RemoteConnection

Command
    ↓
CommandService

Result
    ↓
CommandOutputHandler
```

SIMServe's `RemoteConnection` handles connection-level protocol events.

`CommandService` handles application commands.

This separation should be preserved when adding future functionality.

---

# 12. Versioning

Protocol version is independent from software version.

Current baseline:

```text
SIMServer: 0.1.0
SIMServe:  0.1.0
Protocol:  v1
Client:    not implemented
```

A software release does not necessarily require a protocol version change.

A protocol-breaking change does require a new protocol version.

Future components may therefore have versions such as:

```text
SIMServer  0.5.0
SIMServe   0.5.1
Client     0.3.0
Protocol   v2
```

provided all components support the selected protocol version.

---

# 13. Future Security Model

Protocol v1 does not provide the final production security model.

Current development transport:

```text
ws://
```

Future production communication is expected to provide end-to-end cryptographic protection.

The intended high-level architecture is:

```text
             encrypted payload
Client  ◄────────────────────────► SIMServe
                  │
                  │ routed by
                  ▼
              SIMServer
```

The future Server should primarily route encrypted messages and should not require access to their contents.

Planned security milestones include:

```text
Persistent identity
        ↓
Identity verification
        ↓
Client identity
        ↓
User-approved pairing
        ↓
Authorization
        ↓
Key exchange / synchronization
        ↓
Message authentication
        ↓
End-to-end encryption
```

These mechanisms are not part of Protocol v1.

---

# 14. Compatibility Rule

Server and Serve must implement the same protocol contract.

Protocol changes must be reflected in:

```text
SIMServer
SIMServe
docs/PROTOCOL.md
CHANGELOG.md
DEVELOPER_CHANGELOG.md
```

If a change breaks the existing message contract, the protocol version must be reconsidered before implementation.

---

# 15. Current Protocol Checkpoint

Protocol v1 has been verified end-to-end with:

```text
SIMServer
    ↕
WebSocket
    ↕
SIMServe
```

Verified commands:

```text
summary
history
```

This document represents the protocol baseline for release:

```text
v0.1.0 / Protocol v1
```

Future identity, pairing, authorization, and encryption work should build on this checkpoint or explicitly document why the protocol must change.
