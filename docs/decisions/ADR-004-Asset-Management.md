# ADR-004: Centralized Asset Management with Logical Identifiers

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06-27 |
| **Decision Owner** | Architecture / Engineering |
| **Related** | `04_TRD.md`, `05_ARCHITECTURE.md` |

---

## Context

The game uses images, fonts, sounds, animations, configuration data, and (for future-proofing) localization resources. These must be loaded efficiently to support smooth gameplay and fast transitions, organized clearly, and decoupled from the code that consumes them. The design should also accommodate future downloadable content and new stadiums/teams without structural change.

## Decision

We will use a **centralized Asset Manager** that locates, loads, caches, and serves assets by **logical identifier**, abstracting physical asset location from all consumers. Startup-critical assets load during the Loading state; scene-specific assets load on scene transition.

## Rationale

- **Decoupling:** Consumers request assets by name/identifier, never by path, so content can be reorganized or extended without code edits.
- **Performance:** Centralized caching avoids redundant loading; phased loading (startup vs. scene transition) minimizes stalls and supports smooth gameplay.
- **Extensibility:** New content (DLC, stadiums, teams) is registered through the Asset and Configuration managers as data, enabling additive growth.
- **Maintainability:** A single ownership point for asset lifecycle simplifies reasoning and debugging.

## Asset Categories

- Images, Fonts, Sounds, Animations, Configuration, Localization.

## Loading Strategy

- **Startup-critical assets:** prepared during the Loading state.
- **Scene-specific assets:** prepared during the transition into that scene.
- **Caching:** loaded assets are cached and reused for the session.

## Alternatives Considered

- **Ad-hoc loading by each module:** Causes duplication, inconsistent caching, and tight coupling to file locations; rejected.
- **Eagerly loading everything at startup:** Slows launch and wastes memory; rejected in favor of phased loading.
- **No caching:** Causes redundant work and stutter; rejected.

## Consequences

- **Positive:** Decoupled, cacheable, extensible asset handling that supports performance goals and future content.
- **Negative / trade-offs:** Requires a disciplined identifier scheme and clear ownership; consumers must avoid bypassing the Asset Manager.

## Requirements

- All asset access goes through the Asset Manager.
- Missing assets are detected, logged, and handled gracefully (degrade rather than crash).
- Asset organization remains data-driven to support future expansion.
