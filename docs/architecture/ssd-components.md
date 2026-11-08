# SSD Components

> Details of each component, its responsibilities and dependencies.

---

## 1. MCP Server (`src/mcp/`)

### Responsibilities
- Exposes the 18 MCP tools to the Hermes Agent.
- Translates JSON parameters → calls to the services.
- Formats JSON responses for Hermes.
- Handles errors and returns them as `{"status": "error", ...}`.

### Subcomponents
