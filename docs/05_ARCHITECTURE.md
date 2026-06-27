# Architecture Document — Penalty Shootout

| Field | Value |
|---|---|
| **Product Name** | Penalty Shootout |
| **Genre** | 2D Football Penalty Shootout Game |
| **Platform** | Desktop (Windows, macOS, Linux) |
| **Engine / Stack** | Python + Pygame |
| **Document Type** | Architecture Document (single source of truth) |
| **Document Owner** | Principal Architecture / Engineering |
| **Status** | Draft for Engineering Review |
| **Version** | 1.0 |
| **Date** | 2026-06-27 |

---

## 1. Purpose & Audience

This document is the **architectural source of truth** for Penalty Shootout. It defines how the application is structured, how its parts communicate, how responsibilities are divided, how data and events move, and how the design supports future growth.

It is written so an engineer joining the project for the first time can understand the system without reading any code. It contains **no implementation code, pseudocode, or algorithms** — only the architectural blueprint.

This document answers **"How is the software architected?"** It does not define features (see `01_PRD.md`), navigation (see `02_APP_FLOW.md`), visual design (see `03_UI_UX_BRIEF.md`), engineering standards (see `04_TRD.md`), or scheduling (see `06_IMPLEMENTATION_PLAN.md`).

---

## 2. Architecture Goals

| Goal | Why It Matters |
|---|---|
| **Scalability** | The product must grow (new modes, teams, stadiums, future online features) without structural rewrites. |
| **Maintainability** | Changes should be safe and localized; the architecture optimizes for the cost of change over time. |
| **Readability** | A clear structure lets new contributors orient quickly and reason about the system confidently. |
| **Testability** | Logic must be verifiable in isolation, which requires it to be decoupled from rendering and I/O. |
| **Loose Coupling** | Modules should depend on abstractions and messages, not internals, so they can evolve independently. |
| **High Cohesion** | Related responsibilities live together; unrelated ones stay apart, keeping each unit focused. |
| **Separation of Concerns** | Logic, presentation, data, and I/O are distinct, preventing entanglement and hidden side effects. |
| **Extensibility** | New behavior should be added by composition and subscription, not by editing core code paths. |
| **Reusability** | Shared primitives reduce duplication and accelerate building new features. |
| **Simplicity** | The simplest design that meets requirements reduces risk and is easier to maintain than clever complexity. |

---

## 3. High-Level System Architecture

The application is a single-process, event-driven game built on one central loop. The Application owns lifecycle; the Scene Manager owns the active context; managers provide shared services; game systems hold gameplay logic; the renderer draws from state.

```
                         +--------------------------+
                         |       Application        |
                         |  (entry, lifecycle, loop)|
                         +--------------------------+
                                     |
                                     v
                         +--------------------------+
                         |        Game Loop         |
                         | input -> update -> render|
                         +--------------------------+
                                     |
                 +-------------------+-------------------+
                 |                   |                   |
                 v                   v                   v
        +----------------+  +----------------+  +------------------+
        |  Scene Manager |  |    Managers    |  |   Event Manager  |
        | (active scene) |  | (shared svcs)  |  | (pub/sub bus)    |
        +----------------+  +----------------+  +------------------+
                 |                   |                   ^
   +-------------+-------------+     |                   |
   |             |             |     v                   |
   v             v             v   (Asset, Audio, Input, |
+-------+   +---------+   +---------+ Save, Animation,    |
|Menu   |   |Gameplay |   |Settings | Config managers)    |
|Scene  |   | Scene   |   | Scene   |                     |
+-------+   +----+----+   +---------+                     |
                 |                                        |
                 v                                        |
        +--------------------------+                      |
        |       Game Systems       |----- emit events ----+
        | (ball, keeper, scoring,  |
        |  collision, ai, ...)     |
        +--------------------------+
                 |
                 v
        +--------------------------+
        |        Renderer          |
        |   (reads state, draws)   |
        +--------------------------+
                 |
                 v
        +--------------------------+
        |         Display          |
        +--------------------------+
```

---

## 4. Layered Architecture

The system is organized into logical layers. Dependencies flow **downward only** — higher layers may use lower layers, never the reverse.

```
+-----------------------------------------------------------+
|                  Presentation Layer                       |
|        Scenes, UI, HUD, Renderer (display & intents)      |
+-----------------------------------------------------------+
                          |  (reads state, emits intents)
                          v
+-----------------------------------------------------------+
|                  Game Logic Layer                         |
|   Game Systems & Domain Rules (ball, keeper, scoring,     |
|   tournament, career, achievements, statistics)          |
+-----------------------------------------------------------+
                          |  (uses core constructs)
                          v
+-----------------------------------------------------------+
|                  Core Engine Layer                        |
|   Game Loop, Scene Manager, State Manager, Event Manager  |
+-----------------------------------------------------------+
                          |  (consumes services)
                          v
+-----------------------------------------------------------+
|                   Services Layer                          |
|   Asset, Audio, Input, Animation, Configuration, Logging  |
+-----------------------------------------------------------+
                          |  (persists/restores)
                          v
+-----------------------------------------------------------+
|                 Persistence Layer                         |
|     Save System (settings, stats, achievements,           |
|     tournament & career progress)                         |
+-----------------------------------------------------------+
```

| Layer | Responsibility |
|---|---|
| **Presentation** | Displays the current state and surfaces user intents. Contains no game rules. |
| **Game Logic** | Holds all gameplay rules and is the only layer that mutates game state. |
| **Core Engine** | Provides the loop, scene/state orchestration, and the event bus that wire everything together. |
| **Services** | Cross-cutting capabilities (assets, audio, input, animation, configuration, logging) consumed by upper layers. |
| **Persistence** | Reliably stores and restores durable player data behind a single authority. |

---

## 5. Project Structure

The high-level directory organization mirrors the layers and responsibilities. (Directory purposes only — no file listing.)

```
project_root/
├── core/        # Loop, scene manager, state manager, event manager, timing
├── game/        # Domain rules and orchestration of gameplay
├── scenes/      # Discrete application contexts (splash, menu, gameplay, ...)
├── ui/          # Menus, HUD, dialogs, notifications, presentation components
├── systems/     # Focused gameplay systems (ball, keeper, scoring, ...)
├── managers/    # Shared service coordinators (asset, audio, input, save, ...)
├── assets/      # Images, sounds, fonts, animations, data
├── config/      # Validated configuration values and defaults
├── save/        # Persistence concerns for durable player data
└── utils/       # Dependency-light reusable helpers
```

| Directory | Purpose |
|---|---|
| `core/` | Foundational runtime: the game loop and the orchestration constructs that coordinate everything. |
| `game/` | Domain logic and the coordination of gameplay systems within a match. |
| `scenes/` | Each discrete screen/context as a self-contained unit. |
| `ui/` | Presentation components and HUD that display state and surface intents. |
| `systems/` | Independent gameplay systems with single responsibilities. |
| `managers/` | Long-lived coordinators that own one cross-cutting service each. |
| `assets/` | Categorized game content accessed via the asset manager. |
| `config/` | Centralized, validated configuration and defaults. |
| `save/` | The persistence authority for durable state. |
| `utils/` | Small shared helpers usable across modules without creating coupling. |

---

## 6. Scene Architecture

Scenes are discrete application contexts. The Scene Manager owns exactly one active scene, handles transitions, and routes loop updates and rendering to it. Scenes coordinate their own systems and UI, and communicate outward via managers and events — never by reaching into each other.

```
                         +-------------+
                         |   Splash    |
                         +------+------+
                                |
                                v
                         +-------------+
              +----------|  Main Menu  |-----------+----------------+
              |          +------+------+           |                |
              |                 |                  |                |
              v                 v                  v                v
       +-------------+   +-------------+    +-------------+  +-------------+
       |  Settings   |   |  Tournament |    |   Career    |  | Statistics  |
       +------+------+   +------+------+    +------+------+  +-------------+
              |                 |                  |
              |                 v                  v
              |          +-------------+    +-------------+
              |          | Difficulty/ |    |  (next      |
              |          | Team Select |    |   match)    |
              |          +------+------+    +------+------+
              |                 |                  |
              |                 +--------+---------+
              |                          v
              |                  +-------------+        +-------------+
              |                  |  Gameplay   |<------>|    Pause    |
              |                  +------+------+        +-------------+
              |                          |
              |                          v
              |                  +-------------+
              |                  |   Results   |
              |                  +------+------+
              |                          |
              +--------------------------+----> back to Main Menu / next round
                                         |
                                  +-------------+
                                  |   Credits   |
                                  +-------------+
                                 (from Main Menu)
```

Scene responsibilities at a glance: **Splash** (branding/handoff), **Main Menu** (hub), **Settings** (preferences), **Team/Difficulty Selection** (match setup), **Gameplay** (active match coordination), **Pause** (suspend without state loss), **Results** (outcome + routing), **Tournament** (bracket progression), **Career** (long-term progression), **Statistics** (read-only review), **Credits** (acknowledgment).

---

## 7. Manager Architecture

Managers are long-lived coordinators. Each owns **one** cross-cutting responsibility, coordinates rather than implementing gameplay rules, and exposes a clear interface.

### 7.1 Scene Manager
- **Responsibilities:** Owns the active scene; performs transitions; routes update/render calls.
- **Ownership:** The current scene and the transition lifecycle.
- **Dependencies:** Core (loop, state), Event Manager.
- **Communication rules:** Scenes register/are activated through it; it does not contain gameplay logic.

### 7.2 Asset Manager
- **Responsibilities:** Locate, load, cache, and serve assets by logical identifier.
- **Ownership:** The asset registry and cache.
- **Dependencies:** Configuration, Logging.
- **Communication rules:** Serves any consumer on request; abstracts physical location.

### 7.3 Audio Manager
- **Responsibilities:** Play music, ambience, and effects; manage mix/volume.
- **Ownership:** Audio playback state.
- **Dependencies:** Asset Manager, Configuration, Event Manager.
- **Communication rules:** Reacts to events; holds no gameplay state.

### 7.4 Input Manager
- **Responsibilities:** Capture raw input and translate it into semantic intents.
- **Ownership:** Input mapping and the current intent stream.
- **Dependencies:** Configuration, Core.
- **Communication rules:** Publishes intents to UI and game systems; executes no gameplay logic.

### 7.5 Save Manager
- **Responsibilities:** Persist and restore durable data; validate on load; protect against corruption.
- **Ownership:** All durable player data I/O.
- **Dependencies:** Configuration, Utilities, Logging.
- **Communication rules:** The sole persistence authority; exposes load/save operations.

### 7.6 Animation Manager
- **Responsibilities:** Coordinate timed visual state changes for game and UI elements.
- **Ownership:** Active animation timing and sequencing.
- **Dependencies:** Core (timing), Asset Manager.
- **Communication rules:** Driven by state/events; produces presentation effects only.

### 7.7 Event Manager
- **Responsibilities:** Provide a publish/subscribe bus that decouples producers from consumers.
- **Ownership:** Subscriptions and event dispatch.
- **Dependencies:** Core.
- **Communication rules:** Any module may publish or subscribe; it holds no domain logic.

### 7.8 Configuration Manager
- **Responsibilities:** Provide centralized, validated configuration and defaults.
- **Ownership:** The validated configuration set.
- **Dependencies:** Utilities, Logging.
- **Communication rules:** Read by most modules; authoritative and validated at load.

---

## 8. Game Systems Architecture

Game systems hold gameplay logic, each with a single responsibility. They mutate game state and emit events; consumers react via the Event Manager.

```
        +-----------------------------------------------------------+
        |                        GAME STATE                         |
        |        (authoritative model: score, attempts, etc.)       |
        +-----------------------------------------------------------+
            ^            ^             ^             ^         ^
            |            |             |             |         |
   +--------+----+  +----+-----+  +----+------+  +---+-----+  +-+--------+
   | Shooting    |  | Ball     |  | Goalkeeper|  | Scoring |  | Collision|
   | System      |->| System   |->| System    |->| System  |->| System   |
   +-------------+  +----------+  +-----+-----+  +----+----+  +----------+
         ^                              ^             |
         |                              |             | emits outcome events
   +-----+------+                 +-----+-----+       v
   | Input      |                 | AI System |   +-----------------------+
   | Intents    |                 +-----------+   |     Event Manager     |
   +------------+                                 +-----------+-----------+
                                                              |
            +-------------------+-------------------+---------+---------+
            v                   v                   v                   v
     +-------------+     +-------------+     +-------------+     +-------------+
     | Statistics  |     | Achievement |     | Audio       |     | Animation   |
     | System      |     | System      |     | System      |     | System      |
     +-------------+     +-------------+     +-------------+     +-------------+

     Meta/progression systems (operate across matches):
     +-------------+     +-------------+
     | Tournament  |     | Career      |
     | System      |     | System      |
     +-------------+     +-------------+
```

**Responsibilities:** Shooting (turn intent into a shot), Ball (ball state/movement), Goalkeeper (keeper state/reaction), AI (keeper/opponent decisioning), Collision (contact detection), Physics (motion resolution), Scoring (outcome and score), Animation (visual sequencing), Audio (sound playback), Achievement (condition evaluation), Tournament (bracket progression), Career (long-term progression). Systems remain independent and communicate outcomes through events rather than direct references.

---

## 9. Data Flow

Data flows in one direction during gameplay, keeping logic testable and presentation replaceable.

```
   User Input
       |
       v
+----------------+        (raw -> semantic intents)
| Input Manager  |
+----------------+
       |
       v
+----------------+        (apply rules; only writers of state)
| Game Systems   |
+----------------+
       |
       v
+----------------+        (authoritative model of the match)
|  Game State    |
+----------------+
       |
       v
+----------------+        (reads state; never mutates it)
|   Renderer     |
+----------------+
       |
       v
+----------------+
|    Display     |
+----------------+
```

| Stage | Role |
|---|---|
| **User Input** | Raw device activity from the player. |
| **Input Manager** | Converts raw input into semantic intents. |
| **Game Systems** | Apply rules to intents; the only components that write game state. |
| **Game State** | The single authoritative model of the current match/session. |
| **Renderer** | Reads game state and produces visuals without modifying it. |
| **Display** | The final output presented to the player. |

---

## 10. Event Flow

Events decouple cause from effect. A single trigger fans out to interested systems through the Event Manager.

```
   Button Click / Gameplay Trigger
              |
              v
        +-----------+
        |  Scene /  |   (interprets the trigger in context)
        |  Intent   |
        +-----------+
              |
              v
        +-----------+
        | Game Logic|   (applies rules, produces an outcome)
        +-----------+
              |
              v
        +-------------------+
        |   Event Manager   |  (publishes the outcome)
        +---------+---------+
                  |
   +--------+-----+-----+--------+
   v        v           v        v
+------+ +--------+ +--------+ +-----------+
|Audio | |Animation| |State  | |Statistics/|
|      | |         | |Update | |Achievement|
+------+ +--------+ +--------+ +-----------+
                          |
                          v
                     +---------+
                     | Render  |
                     +---------+
```

Producers emit events without knowing who consumes them; consumers subscribe without knowing who produced them. This keeps audio, animation, statistics, and achievements additive and independent.

---

## 11. State Architecture

The application maintains high-level states with explicit, validated transitions. The State Manager owns the current state; scenes operate within it.

```
 Launch
   |
   v
 Loading ---------> Main Menu <-------------------+
                       |                          |
                       v                          |
                   Gameplay  <----+               |
                    |   |         |               |
            (pause) |   | (goal)  | (resume)      |
                    v   v         |               |
                 Paused  Replay --+               |
                    |   |                          |
            (resume)|   v                          |
                    +-> Gameplay                   |
                       |                           |
                  (match ends)                     |
                       v                           |
                    Result                         |
                       |                           |
                       v                           |
                    Saving --------> (Menu / next)-+
                       |
                       v
                     Exit
```

| State | When It Applies | Typical Transitions |
|---|---|---|
| **Launch** | Process start. | → Loading |
| **Loading** | Startup / scene & asset prep. | → Main Menu / Gameplay |
| **Main Menu** | Navigation hub active. | → Gameplay / Settings / etc. |
| **Gameplay** | Active match. | → Paused / Replay / Result |
| **Paused** | Match suspended. | → Gameplay |
| **Replay** | Qualifying moment replayed. | → Gameplay |
| **Result** | Match concluded. | → Saving |
| **Saving** | Durable data being written. | → Menu / next match |
| **Exit** | Confirmed shutdown. | terminal |

Only legal transitions are permitted; invalid transitions are rejected and logged.

---

## 12. Save Architecture

The Save System (via the Save Manager) is the single authority for durable state. Responsibilities only — no implementation.

```
        +---------------------------------------------+
        |                Save Manager                 |
        |   (validate, persist, restore, protect)     |
        +---------------------------------------------+
          |        |          |           |        |
          v        v          v           v        v
      Settings  Statistics  Achievements  Tournament  Career
                                          Progress    Progress
```

| Domain | Responsibility |
|---|---|
| **Settings** | Persist and restore user preferences. |
| **Statistics** | Persist accumulated performance metrics. |
| **Achievements** | Persist earned and progress-tracked achievements. |
| **Tournament Progress** | Persist in-progress and completed tournament state. |
| **Career Progress** | Persist long-term advancement state. |

The Save Manager validates on load, guards against partial/corrupt writes, and surfaces failures to callers. No other module performs durable player-data I/O.

---

## 13. Asset Architecture

Assets are categorized by type and owned by the Asset Manager, which abstracts location and handles loading and caching.

```
                 +----------------------+
                 |     Asset Manager    |
                 | (registry + caching) |
                 +----------+-----------+
                            |
   +---------+---------+----+----+---------+-------------+
   v         v         v         v         v             v
 Images    Fonts    Sounds   Animations  Config    Localization
```

| Category | Loading / Ownership Notes |
|---|---|
| **Images** | Sprites, backgrounds, icons; loaded and cached on demand or at scene transition. |
| **Fonts** | Typography resources for UI; loaded once and reused. |
| **Sounds** | Music, ambience, effects; served to the Audio Manager. |
| **Animations** | Sequenced visual data driven by the Animation Manager. |
| **Configuration** | Externalized, validated data served via the Configuration Manager. |
| **Localization** | Text resources structured to support future language additions. |

Startup-critical assets load during the Loading state; scene-specific assets load on transition. Consumers request assets by logical identifier, never by physical path.

---

## 14. Dependency Rules

| Rule | Rationale |
|---|---|
| **UI must not directly manipulate game systems.** | UI presents state and emits intents; routing intents through proper channels keeps presentation and logic separable and testable. |
| **Scenes communicate through managers, not each other.** | Prevents scene-to-scene coupling and keeps transitions and shared services centralized. |
| **Managers coordinate but do not own gameplay logic.** | Keeps cross-cutting services reusable and free of domain rules, preserving high cohesion. |
| **Systems remain independent whenever possible.** | Independent systems can be developed, tested, and replaced without ripple effects. |
| **Rendering must not contain business logic.** | A logic-free renderer can be changed or optimized without risking game rules. |
| **Higher layers depend on lower layers only.** | Enforces a clean dependency direction and prevents cycles. |
| **Cross-cutting communication prefers events over direct calls.** | Loose coupling lets new consumers subscribe without modifying producers. |

---

## 15. Communication Rules

```
ALLOWED                              NOT ALLOWED
-------                              -----------
Scene   -> Manager                  UI       -> Save Files
Manager -> System                   Renderer -> AI
System  -> Renderer (via state)     Input    -> Persistence
System  -> Event Manager            Scene    -> Scene (direct)
Any     -> Event Manager (pub/sub)  Renderer -> Game Logic (write)
```

- **Scene → Manager:** Scenes request shared services through managers.
- **Manager → System:** Managers coordinate systems within the active context.
- **System → Renderer (via state):** Systems update state; the renderer reads it.
- **Any ↔ Event Manager:** Publish/subscribe is the preferred decoupled channel.
- **UI ✗ Save Files:** UI never touches persistence directly; it goes through the Save Manager.
- **Renderer ✗ AI / Game Logic:** Rendering reads state only; it never drives logic.
- **Input ✗ Persistence:** Input produces intents; it never writes durable data.
- **Scene ✗ Scene:** Scenes never reference each other directly; they route through managers/events.

---

## 16. Future Expansion

The architecture is designed so the following are **additive** rather than disruptive.

| Future Capability | How the Architecture Enables It |
|---|---|
| **Online multiplayer** | Introduced as a service in the Services layer; game systems stay authoritative and event-driven, so networked input/state sync subscribe to existing events. |
| **FastAPI backend** | A backend client lives in the Services layer behind an interface; gameplay remains unaware of remote concerns. |
| **Cloud saves** | An alternative persistence provider behind the Save Manager interface; callers are unaffected. |
| **Online leaderboards** | A dedicated service plus systems/UI that subscribe to existing outcome events. |
| **Downloadable content** | New assets and data registered via the Asset and Configuration managers. |
| **New stadiums** | Data-driven additions through the asset and configuration layers. |
| **Additional teams** | Data-driven additions; no structural change required. |
| **Additional game modes** | New scenes and systems composed from existing core primitives. |

The common enablers are **layer boundaries**, the **event bus**, **abstracted persistence**, and **data-driven assets/config**.

---

## 17. Architecture Decisions

High-level rationale for major decisions (detailed records live in `docs/decisions/`).

| Decision | Rationale |
|---|---|
| **A Scene Manager exists** | Centralizing the active context and transitions prevents scene-to-scene coupling and provides one place to manage lifecycle and routing. |
| **Managers are separated by concern** | One responsibility per manager yields high cohesion, loose coupling, and reusable services that are easy to test and replace. |
| **Systems are modular** | Single-responsibility systems can evolve independently and be verified in isolation, reducing the blast radius of change. |
| **Game state is centralized** | A single authoritative model removes ambiguity about the source of truth, simplifies rendering, and enables clean testing. |
| **Assets are managed independently** | Abstracting asset location and caching decouples content from code and supports DLC and reorganization without edits. |
| **Communication is event-driven** | Publish/subscribe keeps producers and consumers independent, enabling additive features without modifying existing code. |

---

## 18. Risks & Mitigations

| Risk | Description | Recommendation |
|---|---|---|
| **Tight coupling** | Systems referencing each other's internals become hard to change. | Enforce communication via events/managers; review dependency direction in code review. |
| **Circular dependencies** | Cycles between modules break testability and the layer model. | Keep dependencies flowing downward; introduce abstractions or events to break cycles. |
| **Asset loading bottlenecks** | Loading too much at the wrong time causes stalls. | Load startup-critical assets during Loading; defer scene-specific assets to transitions; cache aggressively. |
| **Large scene classes** | Scenes that absorb logic become unmaintainable "god objects." | Keep scenes as coordinators; push logic into systems and presentation into UI components. |
| **Global state abuse** | Overuse of shared mutable state creates hidden coupling and bugs. | Centralize authoritative state, restrict writers to game systems, and prefer explicit handoffs/events. |
| **Over-engineering** | Speculative abstraction adds complexity without payoff. | Apply KISS; add abstraction only when a concrete need (or a roadmap item with clear seams) justifies it. |

---

## 19. Out of Scope

This document explicitly excludes:

- Feature descriptions (see `01_PRD.md`).
- UI design and UX/navigation decisions (see `03_UI_UX_BRIEF.md`, `02_APP_FLOW.md`).
- Programming code, algorithms, and pseudocode.
- Engineering standards and detailed technical requirements (see `04_TRD.md`).
- Development schedule and sprint planning (see `06_IMPLEMENTATION_PLAN.md`).

---

*End of document.*
