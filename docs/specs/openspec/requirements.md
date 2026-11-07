# Requisitos

> Especificación de requisitos del sistema de tracking de alimentación, economía y entrenamiento.
> Interacción principal: voz → Hermes Agent (MCP) → Sistema.

## Contexto

El sistema corre 24/7 en un PC local (modo servidor). Un agente de IA (Hermes Agent) se conecta
vía MCP server local para ejecutar acciones: registrar comidas, consultar macros, registrar
entrenamientos, consultar PRs, etc. El usuario interactúa por teléfono con Hermes.

## Stack

| Componente | Tecnología |
|-----------|-----------|
| Lenguaje | Python |
| Base de datos | SQLite |
| Integración IA | MCP Server (local)
