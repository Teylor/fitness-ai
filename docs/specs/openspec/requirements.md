# Requirements

> Requirements specification for the nutrition, finance, and workout tracking system.
> Primary interaction: voice → Hermes Agent (MCP) → System.

## Context

The system runs 24/7 on a local PC (server mode). An AI agent (Hermes Agent) connects via a local MCP server to execute actions: logging meals, querying macros, recording workouts, checking PRs, etc. The user interacts with Hermes via phone.

## Stack

| Component | Technology |
|---|---|
| Language | Python |
| Database | SQLite |
| AI Integration | MCP Server (local) |