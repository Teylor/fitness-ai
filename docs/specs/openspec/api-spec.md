# API Specification (MCP Server)

> MCP Tools exposed by the local Python server. Hermes Agent invokes them to interact with the system.

## Conventions

- **Transport**: Local MCP (localhost)
- **Format**: JSON (input and output)
- **Errors**: `{"status": "error", "code": "...", "message": "..."}`
- **Idempotency**: Creation tools check before inserting (fuzzy match) to avoid duplicates.
- **Dates**: `DD-MM-YYYY` for dates, `DD-MM-YYYYTHH:MM:SS` for datetime
- **Units**: `gr` | `ml` | `u`

---

## NUTRITION / FOOD

### `register_meal`

Register an intake (ingredient or recipe). If