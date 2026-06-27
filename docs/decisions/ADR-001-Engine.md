# ADR-001: Game Engine & Technology Stack

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06-27 |
| **Decision Owner** | Architecture / Engineering |
| **Related** | `04_TRD.md`, `05_ARCHITECTURE.md` |

---

## Context

Penalty Shootout is a 2D football penalty shootout game targeting desktop platforms (Windows, macOS, Linux). It must be a polished, portfolio-quality product that demonstrates professional engineering practice. We need a technology foundation that supports 2D rendering, input, audio, a custom game loop, and a clean, testable architecture — while keeping dependencies minimal and the project approachable for portfolio review.

## Decision

We will build the game using **Python with the Pygame framework**, relying on the **Python Standard Library** wherever it suffices and minimizing additional third-party dependencies.

## Rationale

- **Fit for purpose:** Pygame provides windowing, 2D rendering, input, and audio sufficient for a penalty shootout game without unnecessary engine overhead.
- **Architectural control:** A lightweight framework lets us own the game loop and architecture explicitly, which is ideal for demonstrating clean design in a portfolio.
- **Maintainability & readability:** Python's clarity supports the project's readability and maintainability goals and lowers the barrier for reviewers.
- **Cross-platform desktop:** The stack runs across the targeted desktop platforms.
- **Minimal dependency surface:** Preferring the Standard Library keeps the project stable, secure, and easy to reason about.

## Alternatives Considered

- **Full-featured engines (e.g., Unity/Godot):** More built-in features but heavier, less suited to showcasing hand-crafted Python architecture, and beyond the project's needs.
- **Other Python frameworks:** Viable, but Pygame's maturity, ubiquity, and documentation make it the lowest-risk choice for this scope.
- **Web-based stack:** Out of alignment with the desktop, offline, single-player target.

## Consequences

- **Positive:** Full control over architecture; small dependency footprint; clear, reviewable codebase; cross-platform desktop support.
- **Negative / trade-offs:** More foundational systems must be built by hand (loop, scene/state management); performance ceilings are lower than native engines, which is acceptable for this 2D scope.

## Guidelines for Future Dependencies

- Prefer the Standard Library first.
- Evaluate any new dependency on maintenance health, license, footprint, and necessity.
- Isolate third-party usage behind internal abstractions where practical.

This decision does not preclude the Future Vision (backend, online features); those would be added as services behind existing layer boundaries (see `05_ARCHITECTURE.md`).
