# Implementation Plan — Penalty Shootout

| Field | Value |
|---|---|
| **Product Name** | Penalty Shootout |
| **Platform** | Desktop (Windows, macOS, Linux) |
| **Engine / Stack** | Python + Pygame |
| **Document Type** | Implementation Plan (delivery roadmap) |
| **Document Owner** | Technical Lead / Engineering Management |
| **Status** | Draft for Planning Review |
| **Version** | 1.0 |
| **Date** | 2026-06-27 |

---

## 1. Purpose

This document defines **the order in which work is delivered** for Penalty Shootout — phases, milestones, dependencies, and exit criteria. It translates the PRD, App Flow, UI/UX Brief, TRD, and Architecture into an executable sequence.

It answers **"In what order do we build this, and how do we know each part is done?"** It does not redefine features, design, or architecture; those live in the preceding documents.

> Estimates are expressed in relative effort and sequencing, not calendar dates. The team should map phases to a real schedule during sprint planning.

---

## 2. Guiding Delivery Principles

- **Vertical slices first** — get a playable end-to-end loop early, then deepen.
- **Architecture before features** — establish the core skeleton so features attach cleanly.
- **Always shippable** — keep the build runnable at the end of every phase.
- **Polish is a phase, not an afterthought** — reserve explicit time for feel and quality.
- **Test as you go** — core logic is covered while it is being built, not later.

---

## 3. Phase Overview

```
Phase 0  Foundation & Tooling
   ↓
Phase 1  Core Engine Skeleton
   ↓
Phase 2  Minimal Playable Loop (vertical slice)
   ↓
Phase 3  Core Gameplay Systems
   ↓
Phase 4  Menus, Navigation & Scenes
   ↓
Phase 5  Game Modes (Practice, Tournament, Career)
   ↓
Phase 6  Progression, Persistence & Statistics
   ↓
Phase 7  Audio, Animation & Visual Polish
   ↓
Phase 8  Accessibility, QA Hardening & Release Prep
```

---

## 4. Phases & Milestones

### Phase 0 — Foundation & Tooling
- **Goal:** A clean, runnable project foundation with quality tooling in place.
- **Scope:** Repository setup, environment, formatting/linting/type-check tooling, test runner, logging baseline, documentation structure.
- **Dependencies:** None.
- **Exit criteria:** The project runs an empty window; tooling and tests execute in CI; contribution standards are documented.

### Phase 1 — Core Engine Skeleton
- **Goal:** The architectural backbone exists and is testable.
- **Scope:** Game loop, Scene Manager, State Manager, Event Manager, Configuration Manager, Asset Manager (basic), Logging.
- **Dependencies:** Phase 0.
- **Exit criteria:** Scenes can be registered and switched; states transition legally; events publish/subscribe; configuration loads with validation.

### Phase 2 — Minimal Playable Loop (Vertical Slice)
- **Goal:** A player can take a single penalty against a keeper and see an outcome.
- **Scope:** Basic Gameplay scene, Input intents, minimal Ball/Goalkeeper/Shooting/Collision/Scoring, a placeholder result.
- **Dependencies:** Phase 1.
- **Exit criteria:** End-to-end shot → outcome works; the build is playable, however rough.

### Phase 3 — Core Gameplay Systems
- **Goal:** The shootout feels like a real match with difficulty.
- **Scope:** Full shootout flow (multiple attempts, win/loss), goalkeeper behavior with difficulty (Easy/Medium/Hard feel), aiming/power, replay trigger.
- **Dependencies:** Phase 2.
- **Exit criteria:** A complete shootout can be won or lost across all difficulties; replay of a goal works.

### Phase 4 — Menus, Navigation & Scenes
- **Goal:** The full navigation skeleton from the App Flow is in place.
- **Scope:** Splash, Main Menu, Team Selection, Difficulty Selection, Pause, Results, Settings, Credits scenes and transitions; confirmation/exit dialogs.
- **Dependencies:** Phase 3.
- **Exit criteria:** Every screen is reachable per the App Flow with consistent back navigation and no dead ends.

### Phase 5 — Game Modes
- **Goal:** All three modes are playable.
- **Scope:** Practice Mode, Tournament Mode (bracket progression + ceremony), Career Mode (hub + progression across matches).
- **Dependencies:** Phase 4.
- **Exit criteria:** Each mode can be started, played through, and concluded as described in the PRD.

### Phase 6 — Progression, Persistence & Statistics
- **Goal:** Player progress is meaningful and durable.
- **Scope:** Save System (settings, statistics, achievements, tournament, career), Statistics screen, Achievements, unlockables/trophies, persistence at defined moments.
- **Dependencies:** Phase 5.
- **Exit criteria:** Progress persists across sessions; statistics and achievements update correctly; corrupted/missing saves are handled gracefully.

### Phase 7 — Audio, Animation & Visual Polish
- **Goal:** The product reaches its intended premium feel.
- **Scope:** Music, ambience, whistles, kicks, saves, goals, celebrations; menu/transition animations; HUD polish; feedback states.
- **Dependencies:** Phase 6.
- **Exit criteria:** The experience matches the UI/UX Brief's polish and emotional-journey goals; feedback is consistent everywhere.

### Phase 8 — Accessibility, QA Hardening & Release Prep
- **Goal:** A stable, accessible, portfolio-ready build.
- **Scope:** Keyboard navigation, focus states, scalable/readable UI, color-independent feedback; performance validation; regression pass; packaging and final documentation.
- **Dependencies:** Phase 7.
- **Exit criteria:** Success metrics from the PRD are met; the build is stable across supported platforms and presentable for the portfolio.

---

## 5. Milestone Summary

| Milestone | Marks Completion Of | Demonstrable Outcome |
|---|---|---|
| **M1 — Engine Ready** | Phases 0–1 | Scene/state/event skeleton runs and is tested. |
| **M2 — First Kick** | Phase 2 | A single penalty plays end to end. |
| **M3 — Real Match** | Phase 3 | A full shootout across all difficulties. |
| **M4 — Full Navigation** | Phase 4 | All screens reachable per the App Flow. |
| **M5 — All Modes** | Phase 5 | Practice, Tournament, Career playable. |
| **M6 — Persistent Progress** | Phase 6 | Saves, stats, achievements working. |
| **M7 — Polished Build** | Phase 7 | Premium audio/visual feel achieved. |
| **M8 — Release Candidate** | Phase 8 | Stable, accessible, portfolio-ready. |

---

## 6. Cross-Cutting Workstreams

These run throughout all phases rather than as discrete steps:

- **Testing** — unit coverage for logic as it is built; integration and regression tests grow with the system.
- **Documentation** — keep `docs/` aligned as decisions evolve; record new decisions as ADRs.
- **Performance** — monitor frame stability and responsiveness from the first playable build onward.
- **Code review & standards** — enforce the TRD's coding standards and architecture's dependency rules continuously.

---

## 7. Dependencies & Sequencing Rules

- Core engine (Phase 1) **must precede** any gameplay or scene work.
- A vertical slice (Phase 2) **must precede** broad system expansion (Phase 3).
- Navigation (Phase 4) **must precede** game modes (Phase 5), which depend on setup scenes.
- Persistence (Phase 6) **must precede** final polish (Phase 7) so progression feedback can be tuned against real data.
- Accessibility and hardening (Phase 8) **must be last** but should not be the first time accessibility is considered.

---

## 8. Risks to Delivery

| Risk | Impact | Mitigation |
|---|---|---|
| **Scope creep** | Delays a portfolio-quality release. | Hold the line on PRD's "Out of Scope (V1)"; defer extras to Future Vision. |
| **Polish deferred too late** | Product feels unfinished. | Reserve Phase 7 explicitly; apply incremental polish from M2. |
| **Architecture shortcuts under pressure** | Erodes maintainability. | Enforce dependency/communication rules in review; refactor early. |
| **Persistence bugs** | Lost player progress damages trust. | Treat save integrity as a first-class concern with dedicated tests. |
| **Performance regressions** | Breaks the "smooth gameplay" success metric. | Continuous performance checks from the first playable build. |

---

## 9. Definition of Done (Project)

The Version 1 product is considered complete when:

- All PRD core features are implemented and the three modes are playable.
- Navigation matches the App Flow with no dead ends.
- The experience meets the UI/UX Brief's polish and accessibility expectations.
- The implementation respects the TRD standards and the Architecture's rules.
- Progress persists reliably and edge cases are handled gracefully.
- Performance success metrics are met and the build is stable on supported platforms.
- The build is packaged and presentable as a portfolio artifact.

---

## 10. Out of Scope

This plan excludes feature definition (PRD), navigation design (App Flow), visual design (UI/UX Brief), engineering standards (TRD), and architectural blueprint (Architecture). It also excludes Version 2+ roadmap items, which remain future possibilities only.

---

*End of document.*
