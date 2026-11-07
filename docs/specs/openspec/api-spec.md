
# Especificación de API (MCP Server)

> Tools MCP expuestas por el server Python local. Hermes Agent las invoca para interactuar con el sistema.

## Convenciones

- **Transporte**: MCP local (localhost)
- **Formato**: JSON (entrada y salida)
- **Errores**: `{"status": "error", "code": "...", "message": "..."}`
- **Idempotencia**: Las tools de creación buscan antes de insertar (fuzzy match) para evitar duplicados.
- **Fechas**: `DD-MM-YYYY` para fechas, `DD-MM-YYYYTHH:MM:SS` para datetime
- **Unidades**: `gr` | `ml` | `u`

---

## ALIMENTACIÓN

### `register_meal`

Registrar una ingesta (ingrediente o receta). Si
