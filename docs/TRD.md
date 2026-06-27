# Technical Requirements Document — Penalty Shootout

| Field | Value |
|---|---|
| **Product Name** | Penalty Shootout |
| **Genre** | 2D Football Penalty Shootout Game |
| **Platform** | Desktop (Windows, macOS, Linux) |
| **Engine / Stack** | Python + Pygame |
| **Document Type** | Technical Requirements Document (TRD) |
| **Document Owner** | Engineering / Architecture |
| **Status** | Draft for Engineering Review |
| **Version** | 1.0 |
| **Date** | 2026-06-27 |

---

## 1. Purpose & Scope

This document defines the **technical architecture** for Penalty Shootout. It describes how the software should be organized, how responsibilities are separated, how systems communicate, and which architectural decisions should guide development.

It is intended for the engineering team to align on structure **before** implementation begins. It deliberately avoids implementation code, pseudocode, and algorithm design. This document answers a single question: **"How should the software be architected?"**

This TRD complements — and does not duplicate — the PRD (what to build), the App Flow (how users navigate), and the UI/UX Brief (how it looks and feels).

---

## 2. Architectural Goals

The architecture must prioritize, in order of importance:

- **Maintainability** — changes should be safe, localized, and low-risk.
- **Modularity** — systems should be independent, replaceable units.
- **Separation of concerns** — each part of the system has one clear job.
- **Scalability** — new content and features should fit without rework.
- **Readability** — the codebase should be self-explanatory to new contributors.
- **Future extensibility** — Version 2+ features should be additive, not disruptive.

These goals reflect the project's portfolio purpose: the architecture itself is a deliverable that demonstrates professional engineering judgment.

---

## 3. Technical Principles

| Principle | Application to the Project |
|---|---|
| **Single Responsibility Principle (SRP)** | Each module, system, and class should have one reason to change. Gameplay, rendering, input, and persistence must not be entangled. |
| **Separation of Concerns** | Distinct responsibilities (logic, presentation, data, I/O) live in distinct layers and modules. |
| **DRY (Don't Repeat Yourself)** | Shared behavior is centralized; duplication is treated as a defect to be refactored. |
| **KISS (Keep It Simple)** | The simplest design that meets the requirement is preferred over speculative complexity. |
| **Composition over Inheritance** | Behavior should be assembled from focused, reusable components rather than deep inheritance hierarchies, except where inheritance models a genuine "is-a" relationship. |
| **Encapsulation** | Systems expose intent through clear interfaces and hide their internal state and details. |
| **Loose Coupling** | Systems depend on abstractions and messages rather than on each other's internals, so they can evolve independently. |
| **High Cohesion** | Related responsibilities are grouped together; unrelated ones are kept apart. |
| **Readability** | Clear naming and structure take priority over cleverness. |
| **Maintainability** | The architecture optimizes for the cost of change over the lifetime of the product. |

These principles are non-negotiable quality criteria and should inform code review.

---

## 4. High-Level Architecture

The application follows a layered, event-driven game architecture organized around a single central game loop and a scene/state model.

### 4.1 Architectural Layers

- **Application Layer** — the entry point and lifecycle owner; initializes the runtime, owns the game loop, and coordinates top-level managers.
- **Core Layer** — foundational services shared across the product: the game loop, state and scene management, the event system, configuration, and utilities.
- **Domain / Game Systems Layer** — the gameplay logic: ball, goalkeeper, shooting, scoring, collision, replay, tournament, career, achievements, statistics.
- **Presentation Layer** — rendering and UI, responsible only for displaying state and surfacing input intents.
- **Services Layer** — cross-cutting capabilities: audio, save/persistence, asset management, logging.

### 4.2 Key Constructs

- **Application Entry Point** — establishes the runtime, loads configuration, initializes managers, and starts the game loop. It owns startup and shutdown.
- **Game Loop** — the central heartbeat that, each cycle, processes input, advances game logic by the elapsed time, and triggers rendering. It is decoupled from any specific scene.
- **State Management** — governs the high-level application state (e.g., loading, menu, gameplay, paused) and the legal transitions between them.
- **Scene Management** — manages discrete screens/contexts (Splash, Main Menu, Gameplay, etc.), including activation, deactivation, and transitions. The active scene receives loop updates and rendering calls.
- **Managers** — long-lived coordinators (e.g., audio, assets, save, input, scene, state) that own a single cross-cutting responsibility and expose it to the rest of the system.
- **Game Systems** — focused logic units operating within gameplay scenes.
- **Rendering Pipeline** — a presentation pass that draws the current scene and UI from game state; it never mutates game state.
- **Event Handling** — a decoupling mechanism through which systems publish and react to events without holding direct references to one another.

### 4.3 Interaction Model

The game loop drives the active scene. The scene coordinates its game systems and the UI. Input is captured and translated into intents that game systems consume. Game systems mutate game state; the rendering pipeline reads that state to produce visuals; audio and other services react to events emitted by systems. Managers provide shared capabilities to all of the above. Communication between unrelated systems is preferred via the event system rather than direct calls.

---

## 5. Module Breakdown

Each module owns a clear responsibility, a defined set of systems, explicit dependencies, and rules for how it communicates.

### 5.1 Core
- **Responsibility:** Foundational runtime services and orchestration.
- **Owned systems:** Game loop, state manager, scene manager, event system, timing.
- **Dependencies:** Configuration, Utilities, Logging.
- **Communication rules:** May be referenced by most modules; should not depend on domain-specific game systems.

### 5.2 Game (Domain)
- **Responsibility:** All gameplay logic and rules.
- **Owned systems:** Ball, Goalkeeper, Shooting, Collision, Scoring, Replay, Tournament, Career, Achievements, Statistics.
- **Dependencies:** Core (events, state), Configuration, Save System, Utilities.
- **Communication rules:** Emits events for outcomes; must not depend on Rendering or specific UI screens.

### 5.3 UI
- **Responsibility:** Presentation of menus, HUD, dialogs, and notifications; surfacing user intents.
- **Owned systems:** Screen/component composition, HUD presentation, notification surfacing.
- **Dependencies:** Core, Input (intents), Assets, Audio (via events).
- **Communication rules:** Reads game state and emits user intents; must not contain gameplay rules or persistence logic.

### 5.4 Audio
- **Responsibility:** Playback of music, ambience, and sound effects.
- **Owned systems:** Music, ambience, effects, volume/mix control.
- **Dependencies:** Assets, Configuration, Core (events).
- **Communication rules:** Reacts to events; exposes a simple playback interface; holds no gameplay state.

### 5.5 Input
- **Responsibility:** Capturing raw device input and translating it into semantic intents.
- **Owned systems:** Input capture, intent mapping.
- **Dependencies:** Core, Configuration.
- **Communication rules:** Produces intents consumed by UI and Game systems; never executes gameplay logic itself.

### 5.6 Physics
- **Responsibility:** Movement and collision concerns for gameplay objects (e.g., ball trajectory, contact detection).
- **Owned systems:** Motion resolution, collision detection.
- **Dependencies:** Core, Configuration.
- **Communication rules:** Provides results to game systems; remains independent of rendering and UI.

### 5.7 AI
- **Responsibility:** Goalkeeper and opponent behavior decisioning at a system level.
- **Owned systems:** Behavior decisioning, difficulty-driven responses.
- **Dependencies:** Core, Configuration, Game state.
- **Communication rules:** Produces decisions for game systems to act upon; isolated so behaviors can evolve independently.

### 5.8 Animation
- **Responsibility:** Coordinating visual state changes over time for game and UI elements.
- **Owned systems:** Animation timing and sequencing.
- **Dependencies:** Core (timing), Assets.
- **Communication rules:** Driven by state and events; produces presentation effects only.

### 5.9 Save System
- **Responsibility:** Reading and writing persistent player data.
- **Owned systems:** Settings, statistics, achievements, career, tournament persistence.
- **Dependencies:** Configuration, Utilities, Logging.
- **Communication rules:** Exposes load/save operations; the single authority for persistence; no gameplay rules.

### 5.10 Assets
- **Responsibility:** Locating, loading, caching, and providing access to game assets.
- **Owned systems:** Asset registry, loading, caching.
- **Dependencies:** Configuration, Logging.
- **Communication rules:** Serves assets to any module on request; abstracts asset location from consumers.

### 5.11 Configuration
- **Responsibility:** Centralized, validated configuration values and defaults.
- **Owned systems:** Configuration access and validation.
- **Dependencies:** Utilities, Logging.
- **Communication rules:** Read by most modules; treated as authoritative and validated at load.

### 5.12 Utilities
- **Responsibility:** Small, reusable, dependency-light helpers shared across modules.
- **Owned systems:** General-purpose helpers.
- **Dependencies:** Standard Library only (ideally).
- **Communication rules:** May be used widely; must not depend on game-specific modules.

> **Dependency direction:** Presentation depends on Domain and Core; Domain depends on Core and Services; Core depends on Configuration and Utilities. Lower layers must never depend on higher layers. Cross-cutting communication prefers the event system over direct coupling.

---

## 6. Scene Management

Scenes represent discrete application contexts. The scene manager owns the active scene, handles transitions, and routes loop updates and rendering to it. Each scene is responsible for coordinating its own systems and UI and for cleaning up on exit.

| Scene | Responsibility |
|---|---|
| **Splash** | Present branding on launch and hand off to the Main Menu. |
| **Main Menu** | Serve as the navigation hub and route to other scenes. |
| **Settings** | Present and apply preference changes through the Save System. |
| **Team Selection** | Capture the chosen team and pass it forward to gameplay setup. |
| **Difficulty Selection** | Capture the chosen difficulty for the upcoming match or series. |
| **Gameplay** | Coordinate the active match: input intents, game systems, HUD, and outcomes. |
| **Pause** | Suspend gameplay and present in-match options without losing match state. |
| **Results** | Present match outcomes and route to rewards, retry, continue, or menu. |
| **Tournament** | Manage bracket progression and route between rounds and ceremonies. |
| **Career** | Manage long-term progression and route to the next match. |

Scenes communicate setup data forward through a well-defined handoff and emit events for outcomes rather than reaching into other scenes.

---

## 7. Game Systems

Each system has a single, well-bounded responsibility. Implementation details are intentionally excluded.

| System | Responsibility |
|---|---|
| **Ball System** | Owns the state and movement behavior of the ball during play. |
| **Goalkeeper System** | Owns the goalkeeper's state, positioning, and reactions during a shot. |
| **Shooting System** | Translates player aiming and power intent into a shot attempt. |
| **Collision System** | Determines contact between relevant gameplay objects (e.g., ball, goal, keeper). |
| **Scoring System** | Determines and tracks the outcome of each attempt and the match score. |
| **Replay System** | Captures and presents short replays of qualifying moments. |
| **Achievement System** | Evaluates conditions and records earned achievements. |
| **Statistics System** | Aggregates and tracks performance metrics over time. |
| **Tournament System** | Manages bracket structure, progression, and conclusion. |
| **Career Progression** | Manages long-term advancement, history, and state across sessions. |
| **Save System** | Persists and restores all durable state (see §11). |

Systems publish outcomes as events; consumers (UI, audio, statistics, achievements) react without tight coupling.

---

## 8. Data Flow

Information flows in a predictable, unidirectional manner during gameplay:

```
Input (raw device events)
   ↓
Input Intents (semantic actions)
   ↓
Game Logic / Game Systems (rules applied)
   ↓
Game State (authoritative model updated)
   ↓
Rendering Pipeline (reads state → draws)
   ↓
UI (reflects state, surfaces intents)
   ↓
Audio & Notifications (react to emitted events)
```

- Input is captured and converted to intents before reaching game logic.
- Game systems are the only components that mutate game state.
- Rendering and UI read state but never mutate it.
- Audio, statistics, and achievements respond to events emitted by game systems.
- This separation keeps logic testable and presentation replaceable.

---

## 9. State Management

The application maintains a well-defined set of high-level states with controlled transitions.

| State | When It Applies |
|---|---|
| **Loading** | During startup and scene/asset preparation. |
| **Menu** | While in non-gameplay navigation scenes. |
| **Gameplay** | During an active match. |
| **Paused** | When gameplay is suspended via the Pause scene. |
| **Replay** | While a qualifying moment is being replayed. |
| **Match Finished** | When a match concludes and results are presented. |
| **Saving** | While durable state is being persisted. |
| **Exiting** | During confirmed shutdown. |

**Transition rules:** Transitions are explicit and validated; only legal transitions are permitted (e.g., Gameplay → Paused → Gameplay; Gameplay → Match Finished → Saving → Menu). Invalid transitions are rejected and logged. State ownership resides with the state manager, while scenes operate within the active state.

---

## 10. Asset Management

Assets are organized by type and accessed through the Assets module, which abstracts their location from consumers.

- **Images** — sprites, backgrounds, icons, and visual elements.
- **Sounds** — music, ambience, and effects.
- **Fonts** — typography resources used by the UI.
- **Animations** — sequenced visual data driven by the Animation module.
- **Configuration files** — externalized, validated settings and defaults.

**Loading strategy:** Assets required at startup are prepared during the Loading state; assets specific to a scene are prepared during that scene's transition to minimize stalls. Loaded assets are cached and reused to avoid redundant loading. Consumers request assets by logical identifier rather than by physical location, enabling reorganization without code changes.

---

## 11. Save System

The Save System is the single authority for durable state. It owns the responsibility of reliably persisting and restoring the following:

- **Settings** — user preferences (e.g., audio, options).
- **Player statistics** — accumulated performance metrics.
- **Achievements** — earned and progress-tracked achievements.
- **Career progress** — long-term advancement state.
- **Tournament progress** — in-progress and completed tournament state.

**Responsibilities:** Provide clear load and save operations; validate data on load; protect against partial or corrupt writes; and surface failures to callers so the application can respond gracefully. The Save System holds no gameplay rules and is the only module permitted to perform durable I/O for player data.

---

## 12. Error Handling

The application should fail safely and never leave the user stuck.

| Situation | Desired Behavior |
|---|---|
| **Missing assets** | Detect the absence, log it, and degrade gracefully (e.g., fall back where possible) rather than crashing. |
| **Corrupted save file** | Detect invalid data on load, avoid propagating corruption, and offer a safe recovery path (e.g., continue with defaults or a fresh state). |
| **Invalid configuration** | Validate at load, reject invalid values, and fall back to known-good defaults with a clear log entry. |
| **Unexpected failures** | Contain failures at module boundaries, log sufficient context, and keep the application stable where feasible. |

Error handling should be defensive at boundaries (I/O, asset loading, persistence) and the user-facing experience should remain coherent (consistent with the App Flow's edge-case flows).

---

## 13. Logging

Logging exists to support diagnostics, debugging, and operational confidence.

| Event Category | Why It Is Logged |
|---|---|
| **Startup logs** | Confirm initialization order and environment readiness. |
| **Warnings** | Surface recoverable issues (e.g., missing optional asset, fallback applied). |
| **Asset loading** | Trace what was loaded or failed to load, aiding content debugging. |
| **Save operations** | Record load/save attempts and outcomes for data-integrity diagnosis. |
| **Critical errors** | Capture unexpected failures with enough context for root-cause analysis. |

Logging should use clear severity levels, avoid noise in normal operation, and never expose sensitive details. Logs support development and post-release diagnosis without affecting gameplay performance.

---

## 14. Performance Requirements

Performance goals are expressed as outcomes, not techniques.

- **Stable frame rate** — consistent, smooth visual output during gameplay.
- **Responsive input** — actions register without perceptible delay.
- **Fast loading** — startup and scene transitions feel brief.
- **Efficient rendering** — the rendering pass draws only what is needed.
- **Minimal memory usage** — assets and state are managed without unnecessary growth.
- **Smooth gameplay** — no stutter or hitching during high-tension moments.

These goals should be validated through performance testing (see §19) rather than assumed.

---

## 15. Scalability

The architecture must allow future capabilities to be added without major rewrites. Key enablers:

- **Event-driven communication** lets new systems subscribe to existing events without modifying producers.
- **Layered separation** allows the Services layer to gain network-backed implementations behind the same interfaces.
- **Abstracted persistence** allows local saves to be supplemented or replaced by cloud saves behind the Save System interface.
- **Scene/state modularity** allows new modes and screens to be added as new scenes.
- **Asset abstraction** allows new stadiums, teams, and content to be added as data without structural change.

| Future Capability | Architectural Accommodation |
|---|---|
| **Online multiplayer** | Networking introduced as a service; game systems remain authoritative and event-driven. |
| **FastAPI backend** | A backend service consumed via the Services layer, isolated from gameplay logic. |
| **Cloud saves** | An alternative persistence provider behind the Save System interface. |
| **Leaderboards** | A read/write service surfaced through dedicated systems and UI. |
| **Downloadable content** | New assets and data registered through the Assets and Configuration modules. |
| **Additional game modes** | New scenes and systems composed from existing primitives. |
| **New stadiums / teams** | Data-driven additions through the asset and configuration layers. |

---

## 16. Security Considerations

Although Version 1 is offline, the architecture should adopt defensive practices:

- **Save file integrity** — validate structure and content on load; guard against partial writes; avoid trusting persisted data blindly.
- **Configuration validation** — validate all external configuration against expected schemas/ranges and fall back to safe defaults.
- **Defensive programming** — validate inputs at boundaries and handle unexpected states without crashing.
- **Safe file handling** — handle file operations defensively, anticipate missing or unreadable files, and avoid destructive operations on failure.

These practices also lay groundwork for safe handling of remote data in future versions.

---

## 17. External Dependencies

Dependencies should be minimal, well-justified, and stable.

- **Pygame** — the primary game framework for windowing, rendering, input, and audio.
- **Python Standard Library** — preferred for general functionality to limit third-party surface area.

**Guidelines for future dependencies:**
- Prefer the Standard Library where it suffices.
- Evaluate any new dependency on maintenance health, license compatibility, footprint, and necessity.
- Avoid dependencies that duplicate existing capabilities or introduce significant complexity.
- Isolate third-party usage behind internal abstractions where practical, to limit coupling.

---

## 18. Coding Standards

Project-wide engineering standards (stated as expectations, not code):

- **Naming conventions** — consistent, descriptive names for modules, systems, and identifiers.
- **File organization** — modules grouped by responsibility; one clear concern per unit.
- **Documentation** — public interfaces and modules carry clear, purposeful documentation.
- **Comments** — explain intent and rationale where non-obvious; avoid restating the obvious.
- **Formatting** — consistent, automated formatting applied across the codebase.
- **Type hints** — used to clarify interfaces and support tooling.
- **Error handling** — consistent, intentional handling at boundaries with appropriate logging.
- **Testing expectations** — systems are designed to be testable; critical logic is covered (see §19).

Standards should be enforced through code review and automated tooling.

---

## 19. Testing Strategy

Testing philosophy emphasizes confidence in core logic and stability of the player experience.

- **Unit testing** — verify the behavior of individual systems (e.g., scoring, progression rules) in isolation. Logic should be designed to be testable independent of rendering.
- **Integration testing** — verify that systems cooperate correctly across boundaries (e.g., gameplay outcomes flowing into statistics, achievements, and persistence).
- **Manual gameplay testing** — validate feel, responsiveness, and polish, which automated tests cannot fully capture.
- **Regression testing** — guard against reintroducing fixed defects as the product evolves.
- **Performance testing** — validate the performance goals in §14 under representative conditions.

The separation of logic from presentation is a deliberate enabler of automated testing.

---

## 20. Future Technical Roadmap

These are forward-looking possibilities only; they must not influence Version 1 scope.

**Version 2**
- FastAPI backend service.
- Authentication.
- Cloud saves.

**Version 3**
- Online multiplayer.
- Matchmaking.
- Leaderboards.

**Version 4**
- Broader cross-platform support.
- Storefront/distribution integration (e.g., Steam).

The Version 1 architecture should keep these directions viable as additive changes behind existing layer boundaries.

---

## 21. Out of Scope

This document explicitly excludes:

- UI design and visual styling (see UI/UX Brief).
- UX and navigation decisions (see App Flow).
- Implementation code, algorithms, and pseudocode.
- Feature definition and prioritization (see PRD).
- Project scheduling and task sequencing (see Implementation Plan).

---

*End of document.*
