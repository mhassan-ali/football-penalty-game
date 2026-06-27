# ADR-002: Layered, Event-Driven Architecture with Scene & Manager Model

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06-27 |
| **Decision Owner** | Architecture / Engineering |
| **Related** | `04_TRD.md`, `05_ARCHITECTURE.md` |

---

## Context

The project must be scalable, maintainable, modular, and testable, and it must accommodate future features (additional modes, content, and eventually online capabilities) without major rewrites. We need an overarching structural pattern that divides responsibilities cleanly and controls how parts communicate.

## Decision

We will adopt a **layered architecture** (Presentation → Game Logic → Core Engine → Services → Persistence) combined with a **scene-based** organization of application contexts, **single-responsibility managers** for cross-cutting services, and an **event-driven** communication model via a central event bus.

## Rationale

- **Separation of concerns:** Layers keep logic, presentation, services, and persistence distinct, preventing entanglement.
- **Loose coupling / high cohesion:** Managers own one concern each; systems communicate through events rather than direct references, so parts evolve independently.
- **Testability:** Game logic is decoupled from rendering and I/O, enabling unit testing of rules in isolation.
- **Extensibility:** New scenes, systems, and consumers attach via composition and subscription without editing existing code paths.
- **Predictable data flow:** A single authoritative game state with unidirectional data flow removes ambiguity about the source of truth.

## Alternatives Considered

- **Monolithic loop with intermingled logic and rendering:** Simpler initially but quickly becomes unmaintainable and untestable; rejected.
- **Pure inheritance hierarchies for game objects:** Leads to rigid, deep hierarchies; we prefer composition over inheritance where appropriate.
- **Direct system-to-system calls instead of events:** Increases coupling and makes additive features costly; rejected in favor of pub/sub.

## Consequences

- **Positive:** Clean dependency direction, modular systems, strong testability, and a clear path to future expansion behind layer boundaries.
- **Negative / trade-offs:** More upfront structure (managers, event bus, state model) than a naive approach; requires discipline to keep scenes thin and avoid coupling. Mitigated through code review and the dependency/communication rules in `05_ARCHITECTURE.md`.

## Enforcement

- Dependencies flow downward only; no circular dependencies.
- Cross-cutting communication prefers the event bus.
- Scenes coordinate; they do not own gameplay logic.
- Rendering reads state and never mutates it.
