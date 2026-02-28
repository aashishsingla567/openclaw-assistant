# ADR 0002: Stage Contract Validation

## Status
Accepted

## Decision
Validate required methods for each plugin stage at startup in `PluginRegistry.validate()`.

## Consequences
- Fail fast for invalid plugin wiring.
- Reduced runtime surprises for new developers.
