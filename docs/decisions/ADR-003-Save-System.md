# ADR-003: Local Save System as Single Persistence Authority

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-06-27 |
| **Decision Owner** | Architecture / Engineering |
| **Related** | `01_PRD.md`, `04_TRD.md`, `05_ARCHITECTURE.md` |

---

## Context

Version 1 is an offline, single-player desktop game. It must persist user preferences, statistics, achievements, tournament progress, and career progress across sessions using local storage only. Persistence must be reliable, validated, and resilient to missing or corrupted data, and it must not be entangled with gameplay logic. The design should also leave room for future cloud-based persistence.

## Decision

We will implement a **single Save System (owned by a Save Manager)** that is the **sole authority** for all durable player-data input/output, using **local save files** for Version 1. All persistence flows through this module behind a clear load/save interface.

## Rationale

- **Single source of truth for persistence:** Centralizing durable I/O prevents scattered, inconsistent file access and makes data integrity manageable.
- **Separation of concerns:** Gameplay systems produce data; only the Save System persists it, keeping rules free of I/O.
- **Resilience:** A single authority can uniformly validate on load, guard against partial/corrupt writes, and surface failures gracefully.
- **Future-proofing:** An abstracted interface allows cloud saves to be added later as an alternative provider without changing callers (see Future Vision).
- **Constraint alignment:** Local files satisfy the offline, single-player Version 1 constraints.

## Scope of Persisted Data

- Settings (user preferences)
- Player statistics
- Achievements
- Tournament progress
- Career progress

## Alternatives Considered

- **Direct file access from multiple modules:** Causes inconsistency, coupling, and integrity risks; rejected.
- **A backend/cloud store for Version 1:** Violates the offline constraint and adds unnecessary complexity; deferred to Future Vision.
- **In-memory only (no persistence):** Fails progression requirements; rejected.

## Consequences

- **Positive:** Reliable, validated, centralized persistence; clean separation from gameplay; a clear seam for future cloud saves.
- **Negative / trade-offs:** All durable data must route through one module, requiring disciplined interfaces; corruption and edge cases must be handled deliberately (covered by error-handling expectations in the TRD and App Flow).

## Requirements

- Validate data on load; never propagate corruption.
- Protect against partial writes.
- Save at defined moments (end of match, achievement unlocked, settings changed, tournament completed, career updated).
- Surface failures to callers so the application can respond gracefully.
