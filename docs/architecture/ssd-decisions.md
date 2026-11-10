# Architecture Decisions (ADR)

> Registry of architectural decisions. Each ADR: context, decision, consequences.

---

## ADR-001: Python + SQLite + Peewee

**Date**: 2025-01-15
**Status**: Accepted

### Context
Single-user local system. There is no scalability requirement. Simplicity and minimal overhead are required.

### Decision
- **Language**: Python 3.11+
- **Database**: SQLite 3 (local file `data/fitness.db`)
- **ORM**: Peewee (lightweight, no heavy dependencies like SQLAlchemy)
- **Migrations**: `peewee-migrate` + manual SQL scripts

### Consequences
- ✅ Zero external infrastructure. A single `.db` file is all the persistence.
- ✅ Peewee is minimalist, easy to debug, no magic.
- ✅ Simple migrations for a single user.
- ❌ Not scalable to multi-user (not a requirement).
- ❌ No replicas

---

## ADR-002: Project language is English

**Date**: 2026-11-08
**Status**: Accepted

### Context
All project artifacts (docs, specs, ODD, ADRs, READMEs, code comments/docstrings, test descriptions, SQL and script comments) were written in Spanish. To keep the codebase consistent and broadly readable, the project standardizes on a single language.

### Decision
- All project artifacts are written in **English**: docs, specs, architecture, ODD, ADRs, READMEs, code comments/docstrings, test docstrings/assertion messages, SQL comments, and script comments.
- Code identifiers, imports, syntax, and technical terms are unaffected (they already follow Python/SQL conventions).
- Existing Spanish content is migrated to English by the `translate-to-english` feature; no new Spanish content is added from now on.

### Consequences
- ✅ One consistent language across the whole project.
- ✅ New readers/contributors need no Spanish.
- ⚠️ Test fixtures that intentionally exercise accent/normalization behavior (e.g. `normalize("Café")`, `normalize("Ñandú")`) are preserved as-is, because the accented input is the point of those tests.

---

## ADR-003: Mobile Access Strategy (Android APK & Remote API)

**Date**: 2026-11-10  
**Status**: Proposed / Evaluated (Low Priority P3)

### Context
The application is currently served locally on `localhost:9700` with an embedded HTML/JS single-page interface and SQLite backend. The user requested an architectural assessment for accessing the app on Android devices remotely (outside the home network) as an installable `.apk`.

### Decision
When this capability is scheduled for implementation:

1. **Mobile Packaging (Android APK)**:
   - **Strategy**: Hybrid web wrapper using **Capacitor** (or Trusted Web Activity / Bubblewrap) or Progressive Web App (PWA).
   - **Rationale**: Reuses 100% of the existing responsive web dashboard (`src/ui/html_generator.py`). Avoids the high development cost (~2-3 weeks) of rewriting the frontend in Flutter or React Native.
   - **Artifact**: Produces a standard Android `.apk` installable on user devices.

2. **Remote Access & Networking**:
   - **Primary Approach (Zero Infrastructure Cost)**: **Cloudflare Tunnel (`cloudflared`)** with **Cloudflare Zero Trust Access**.
     - Provides automatic HTTPS (required by Android web views).
     - Exposes the local Starlette/FastMCP server without port forwarding or dynamic DNS.
     - Offloads authentication to Cloudflare Access (e.g., Google login gate) before traffic hits the local server.
   - **Alternative (Private Mesh)**: **Tailscale** for direct encrypted peer-to-peer connection without public exposure.
   - **Cloud VPS Alternative**: A lightweight cloud VPS (e.g. Hetzner, Railway) with persistent disk volume if 24/7 availability without relying on the desktop PC is desired.

3. **Backend Requirements**:
   - Enable CORS headers on `/api/*` for mobile origin requests.
   - Enforce HTTPS (required by Android cleartext policies).

### Consequences
- ✅ Low implementation cost (~1 day of work).
- ✅ Zero code duplication between web and mobile interfaces.
- ✅ Flexible hosting: can start with zero-cost Cloudflare Tunnel and migrate to cloud VPS later if needed.

