# Componentes SSD

> Detalle de cada componente, sus responsabilidades y dependencias.

---

## 1. MCP Server (`src/mcp/`)

### Responsabilidades
- Expone las 18 tools MCP a Hermes Agent.
- Traduce parámetros JSON → llamadas a Services.
- Formatea respuestas JSON para Hermes.
- Maneja errores y los devuelve como `{"status": "error", ...}`.

### Subcomponentes
