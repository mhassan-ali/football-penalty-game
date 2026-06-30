# Penalty Shootout — Documentation

This directory is the documentation set for **Penalty Shootout**, a 2D football penalty shootout game (Python + Pygame, desktop). The documents are ordered to be read in sequence, moving from **what** the product is to **how** it is architected and delivered.

## Core Documents

| # | Document | Answers |
|---|---|---|
| 01 | [`01_PRD.md`](01_PRD.md) | What we are building and why (product requirements). |
| 02 | [`02_APP_FLOW.md`](02_APP_FLOW.md) | How the user moves through the application (navigation & journeys). |
| 03 | [`03_UI_UX_BRIEF.md`](03_UI_UX_BRIEF.md) | What the product should look and feel like (design vision). |
| 04 | [`04_TRD.md`](04_TRD.md) | Engineering standards and technical requirements. |
| 05 | [`05_ARCHITECTURE.md`](05_ARCHITECTURE.md) | How the software is architected (the blueprint, source of truth). |
| 06 | [`06_IMPLEMENTATION_PLAN.md`](06_IMPLEMENTATION_PLAN.md) | In what order we build it and how we know each part is done. |

## Decisions (ADRs)

Architecture Decision Records capturing major, durable choices.

- [`decisions/ADR-001-Engine.md`](decisions/ADR-001-Engine.md) — Game engine & technology stack.
- [`decisions/ADR-002-Architecture.md`](decisions/ADR-002-Architecture.md) — Layered, event-driven architecture.
- [`decisions/ADR-003-Save-System.md`](decisions/ADR-003-Save-System.md) — Local save system as single persistence authority.
- [`decisions/ADR-004-Asset-Management.md`](decisions/ADR-004-Asset-Management.md) — Centralized asset management.

## References

Supporting, non-authoritative working notes.

- [`references/art-direction.md`](references/art-direction.md)
- [`references/inspiration.md`](references/inspiration.md)
- [`references/gameplay-notes.md`](references/gameplay-notes.md)
- [`references/technical-research.md`](references/technical-research.md)

## Diagrams

Visual companions to the documents (dark-themed PNGs).

- `diagrams/app-flow.png` — application navigation flow.
- `diagrams/architecture.png` — layered architecture.
- `diagrams/state-machine.png` — application state machine.
- `diagrams/module-diagram.png` — module & system relationships.

---

*Reading order: 01 → 02 → 03 → 04 → 05 → 06. Decisions and references support the core documents; diagrams illustrate them.*
