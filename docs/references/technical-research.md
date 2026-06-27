# Reference — Technical Research

| Field | Value |
|---|---|
| **Document Type** | Reference (supporting notes) |
| **Status** | Living reference |
| **Date** | 2026-06-27 |
| **Related** | `04_TRD.md`, `05_ARCHITECTURE.md`, `docs/decisions/` |

> Supporting research notes that inform the technical decisions recorded in the TRD, Architecture, and ADRs. These are non-authoritative working notes; final decisions live in the ADRs.

---

## 1. Topics Under Investigation

| Topic | Why It Matters | Status |
|---|---|---|
| Game loop & timing model | Stable frame rate and responsive input are success metrics. | Informs Architecture §3, §9 |
| Scene & state management approach | Clean navigation and no dead ends depend on it. | Informs Architecture §6, §11 |
| Event/messaging model | Loose coupling and extensibility hinge on this. | Informs Architecture §10 |
| Asset loading & caching strategy | Fast loading and smooth gameplay. | Captured in ADR-004 |
| Persistence approach & integrity | Reliable progress, graceful corruption handling. | Captured in ADR-003 |
| Testing strategy for game logic | Testability goal requires logic decoupled from rendering. | Informs TRD §19 |

## 2. Key Findings (Directional)

- **Decouple logic from rendering** to make core systems unit-testable; this is a recurring best practice for maintainable game code and aligns with the project's testability goal.
- **Centralized, validated configuration and assets** reduce coupling and support data-driven content growth (DLC, teams, stadiums).
- **A single persistence authority with validation** is the most reliable way to protect player progress and to leave room for future cloud saves.
- **Event-driven communication** is the lowest-coupling way to let audio, animation, statistics, and achievements react to gameplay without entangling systems.

## 3. Constraints Confirmed

- Python + Pygame, desktop, offline, single-player for Version 1 (see ADR-001).
- Minimal third-party dependencies; prefer the Standard Library.
- Local save files only for Version 1.

## 4. Future-Facing Research (Not Version 1)

- Backend service patterns (e.g., a FastAPI service) for accounts, cloud saves, and leaderboards — to be added behind the Services layer.
- Networking/synchronization considerations for eventual online multiplayer.
- Cross-platform packaging and distribution (e.g., storefront release).

These are recorded only to confirm that the Version 1 architecture leaves clean seams for them; they must not influence Version 1 scope.

## 5. Open Questions

- Performance validation approach and target conditions for the success metrics.
- Packaging strategy across Windows/macOS/Linux.
- Localization data structure to support future languages without rework.

*Update this document as research progresses and promote settled decisions into ADRs.*
