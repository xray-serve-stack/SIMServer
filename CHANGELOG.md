# Changelog

All notable changes to SIMServer are documented here.

## [0.1.0] - 2026-09-11

### Added

- Initial SIMServer WebSocket server.
- WebSocket endpoint for SIMServe connections.
- Serve registration handshake.
- Server-generated `serve_id`.
- Active Serve connection management through `ServeManager`.
- Pending request tracking using `request_id`.
- HTTP command endpoint for routing commands to a selected Serve.
- Standardized Command message format.
- Standardized Result message format.
- `summary` command routing.
- `history` command routing.
- Command/result correlation using `request_id`.
- Development mock Serve for protocol testing.

### Protocol

Introduced Protocol v1 with:

- `register`
- `registered`
- `command`
- `result`

The protocol uses the same Command/Result contract between SIMServer and SIMServe.

### Testing

Verified:

- SIMServe ↔ SIMServer WebSocket connection.
- Serve registration.
- Server-generated `serve_id`.
- Command transmission.
- Command execution on a real Android SIMServe device.
- Result transmission back to SIMServer.
- `summary` end-to-end execution.
- `history` end-to-end execution.
- Multiple Serve connection handling during development.

### Current Limitations

The following are intentionally not implemented:

- Persistent Serve identity.
- Client application.
- Serve ↔ Client pairing.
- Authorization.
- Authentication.
- Cryptographic identity.
- End-to-end encryption.
- Production security model.

### Checkpoint

`v0.1.0` is the baseline development checkpoint for the stable Server ↔ Serve communication pipeline.

The next planned milestone is persistent Serve identity.
