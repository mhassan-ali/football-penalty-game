# Application Flow Document — Penalty Shootout

| Field | Value |
|---|---|
| **Product Name** | Penalty Shootout |
| **Genre** | 2D Football Penalty Shootout Game |
| **Platform** | Desktop (Windows, macOS, Linux) |
| **Document Type** | Application Flow Document (APP_FLOW) |
| **Document Owner** | Product Design / UX |
| **Status** | Draft for Design & Engineering Review |
| **Version** | 1.0 |
| **Date** | 2026-06-27 |

---

## 1. Purpose

This document defines **how users move through the Penalty Shootout application** from launch to exit. It describes every screen, the actions available on each, the transitions between them, and the user journeys that connect them.

It is written for UI/UX designers and software engineers to establish a shared understanding of navigation **before** development begins. It deliberately excludes UI design, visual styling, and implementation details — those belong in later documents.

This document answers a single question: **"How does the user move through the application?"**

---

## 2. High-Level Flow Diagram

```
Launch Game
    ↓
Splash Screen
    ↓
Main Menu  ←──────────────────────────────┐
    ↓                                      │
Select Game Mode                           │
    ↓                                      │
 ┌──────────────┬──────────────┬───────────────┐
 │              │              │               │
Practice    Tournament      Career         (other menu
 │              │              │            destinations:
 │         Team Select    Continue/New        Settings,
 │              │           Career            Statistics,
Difficulty   Difficulty       │             Achievements,
 │              │              │              Credits)
 ↓              ↓              ↓                 │
Match Loading                                   │
    ↓                                           │
Gameplay  ←──── Pause Menu (ESC)                │
    ↓                                           │
Goal Replay (on goal)                           │
    ↓                                           │
Match Result                                    │
    ↓                                           │
Rewards / Progression Update                    │
    ↓                                           │
(Continue series, Retry, or Return) ────────────┘
    ↓
Exit Confirmation
    ↓
Quit Application
```

> All non-gameplay screens provide a consistent path back toward the Main Menu. No screen is a dead end.

---

## 3. Screen Inventory

Each screen is documented with its purpose, entry points, exit points, and the actions a user can take.

### 3.1 Splash Screen
- **Purpose:** Display branding on launch and signal that the application is starting.
- **Entry Point:** Application launch.
- **Exit Points:** Main Menu.
- **User Actions:** Wait for automatic transition; optionally skip/dismiss to proceed to the Main Menu.

### 3.2 Main Menu
- **Purpose:** Central hub from which all major destinations are reached.
- **Entry Point:** Splash Screen; return from any mode, results, or sub-screen.
- **Exit Points:** Select Game Mode (Practice / Tournament / Career), Settings, Statistics, Achievements, Credits, Exit Confirmation.
- **User Actions:** Choose a game mode; open Settings; view Statistics; view Achievements; view Credits; quit the game.

### 3.3 Game Mode Selection
- **Purpose:** Let the user choose how they want to play.
- **Entry Point:** Main Menu.
- **Exit Points:** Team Selection / Difficulty Selection (per mode requirements), Career Mode hub, Back to Main Menu.
- **User Actions:** Select Practice, Tournament, or Career; go back.

### 3.4 Team Selection
- **Purpose:** Choose the team the player will represent for the match or series.
- **Entry Point:** Game Mode Selection (Tournament / applicable modes).
- **Exit Points:** Difficulty Selection (or next required step), Back to previous screen.
- **User Actions:** Browse and select a team; confirm selection; go back.

### 3.5 Difficulty Selection
- **Purpose:** Set the challenge level for the upcoming match or series.
- **Entry Point:** Team Selection; Game Mode Selection (modes that set difficulty directly).
- **Exit Points:** Match Loading (or series start), Back to previous screen.
- **User Actions:** Choose Easy, Medium, or Hard; confirm; go back.

### 3.6 Tournament Selection / Bracket Screen
- **Purpose:** Present the tournament structure, current round, and progress toward the final.
- **Entry Point:** Game Mode Selection (Tournament); return after each tournament match result.
- **Exit Points:** Match Loading (next round), Champion Ceremony (after final), Tournament Statistics, Main Menu (with confirmation if a tournament is in progress).
- **User Actions:** Start or continue to the next match; view bracket progress; abandon tournament (with confirmation).

### 3.7 Career Mode Hub
- **Purpose:** Manage and progress a long-term career, including continuing or starting a career.
- **Entry Point:** Game Mode Selection (Career).
- **Exit Points:** Match Loading (play next match), Statistics, Rewards/Progress view, Main Menu.
- **User Actions:** Continue career; start a new career; play next match; review career progress; go back.

### 3.8 Match Loading
- **Purpose:** Brief transition that prepares the user for the upcoming match.
- **Entry Point:** Difficulty Selection; Tournament Bracket; Career Hub.
- **Exit Points:** Gameplay.
- **User Actions:** Wait for automatic transition.

### 3.9 Gameplay (Match Screen)
- **Purpose:** The core penalty shootout experience where the user takes and/or defends penalties.
- **Entry Point:** Match Loading.
- **Exit Points:** Goal Replay (on a goal), Pause Menu (on pause), Match Result (when the shootout concludes).
- **User Actions:** Take a shot; defend a shot; pause the match.

### 3.10 Goal Replay
- **Purpose:** Provide a short, rewarding replay of a notable moment such as a goal.
- **Entry Point:** Gameplay (triggered by a qualifying event).
- **Exit Points:** Return to Gameplay (continue the shootout).
- **User Actions:** Watch the replay; optionally skip to continue play.

### 3.11 Match Result
- **Purpose:** Communicate the outcome of the match and summarize performance.
- **Entry Point:** Gameplay (shootout concluded).
- **Exit Points:** Rewards / Progression Update; Retry Match; Continue (next round / next career match); Return to Main Menu.
- **User Actions:** Proceed to rewards/progression; retry the match; continue a series; return to the menu.

### 3.12 Rewards / Progression Update
- **Purpose:** Present rewards earned and reflect updated progression (trophies, unlocks, stats, achievements).
- **Entry Point:** Match Result.
- **Exit Points:** Tournament Bracket (if in a tournament), Career Hub (if in career), Main Menu.
- **User Actions:** Acknowledge rewards; continue to the next appropriate screen.

### 3.13 Statistics
- **Purpose:** Display tracked performance data. Read-only; never modifies game data.
- **Entry Point:** Main Menu; Career Hub; Tournament flow (Tournament Statistics).
- **Exit Points:** Back to the screen that opened it.
- **User Actions:** View statistics; go back.

### 3.14 Achievements
- **Purpose:** Display earned and available achievements. Read-only.
- **Entry Point:** Main Menu.
- **Exit Points:** Back to Main Menu.
- **User Actions:** Browse achievements; go back.

### 3.15 Settings
- **Purpose:** Adjust preferences such as audio and other available options.
- **Entry Point:** Main Menu; Pause Menu.
- **Exit Points:** Back to the screen that opened it (Main Menu or Pause Menu), with save/discard handling.
- **User Actions:** Modify options; save changes; discard/cancel; go back.

### 3.16 Pause Menu
- **Purpose:** Pause an active match and offer in-match navigation options.
- **Entry Point:** Gameplay (ESC / pause action).
- **Exit Points:** Resume to Gameplay; Restart Match; Settings; Return to Main Menu (with confirmation).
- **User Actions:** Resume; restart the match; open Settings; quit to Main Menu.

### 3.17 Confirmation Dialogs
- **Purpose:** Confirm potentially destructive or progress-affecting actions before they occur.
- **Entry Point:** Triggered by actions such as quitting a match, abandoning a tournament, exiting the game, or discarding settings.
- **Exit Points:** Proceed with the action; cancel and remain on the current screen.
- **User Actions:** Confirm; cancel.

### 3.18 Credits
- **Purpose:** Acknowledge contributors.
- **Entry Point:** Main Menu.
- **Exit Points:** Back to Main Menu.
- **User Actions:** View credits; go back.

### 3.19 Exit Confirmation
- **Purpose:** Confirm the user's intent to quit the application.
- **Entry Point:** Main Menu (Quit); global exit action.
- **Exit Points:** Quit application; cancel and return to Main Menu.
- **User Actions:** Confirm exit; cancel.

---

## 4. User Journeys

### 4.1 First-Time User
```
Launch
   ↓
Splash Screen
   ↓
Main Menu
   ↓
Settings (optional — adjust audio/preferences)
   ↓
Game Mode Selection → Practice
   ↓
Difficulty Selection
   ↓
Match Loading
   ↓
Gameplay
   ↓
Match Result
   ↓
Return to Main Menu
```
A first-time user can reach gameplay quickly. Settings are optional and do not block access to play.

### 4.2 Tournament Player
```
Launch
   ↓
Main Menu
   ↓
Game Mode Selection → Tournament
   ↓
Team Selection
   ↓
Difficulty Selection
   ↓
Tournament Bracket → Quarter Final
   ↓
Match → Result → Rewards → Tournament Bracket
   ↓
Semi Final
   ↓
Match → Result → Rewards → Tournament Bracket
   ↓
Final
   ↓
Match → Result → Champion Ceremony
   ↓
Tournament Statistics
   ↓
Main Menu
```
Each round returns to the bracket, where progress is shown before advancing to the next match.

### 4.3 Career Player
```
Launch
   ↓
Main Menu
   ↓
Game Mode Selection → Career
   ↓
Career Hub → Continue Career
   ↓
Play Match
   ↓
Match Result
   ↓
Rewards / Progression Update
   ↓
Career Hub (updated progress, auto-saved)
   ↓
Exit (to Main Menu or quit)
```
Career progress is updated and saved as the player advances, so the next session can resume from where they left off.

### 4.4 Settings Flow
```
Main Menu (or Pause Menu)
   ↓
Settings
   ↓
Modify Options
   ↓
Save
   ↓
Return to the originating screen
```
Settings always return the user to the screen from which they were opened.

### 4.5 Pause Flow
```
Gameplay
   ↓
Pause Menu (ESC)
   ↓
 ┌──────────────┬──────────────────┬──────────────────────┐
 │              │                  │                      │
Resume     Restart Match      Settings          Return to Main Menu
 │              │                  │              (Confirmation Dialog)
 ↓              ↓                  ↓                      ↓
Gameplay   Match Loading      Settings → back        Main Menu
                                to Pause
```

---

## 5. Navigation Rules

- **ESC** opens the Pause Menu during gameplay; during a Goal Replay it skips/returns to gameplay; on menu screens it triggers Back.
- **Back** always returns to the immediately previous screen, with consistent behavior across the application.
- **Exit** the application always requires confirmation.
- **Settings** are accessible from both the Main Menu and the Pause Menu and always return to their point of origin.
- **Statistics** are read-only and never modify game data.
- **Achievements** are read-only.
- **Goal Replay** is a transient state that always returns control to active gameplay.
- **Destructive or progress-affecting actions** (quit match, abandon tournament, exit game, discard settings) require a confirmation dialog.
- **No screen is a dead end** — every screen offers a clear path forward and a path back.

---

## 6. Screen States

| State | When It Occurs |
|---|---|
| **Loading** | During Splash Screen and Match Loading transitions while content is being prepared. |
| **Idle** | On menu and selection screens awaiting user input. |
| **In Match** | During active gameplay when penalties are being taken or defended. |
| **Paused** | When the user opens the Pause Menu during a match; gameplay is suspended. |
| **Goal Replay** | When a qualifying moment triggers a short replay; gameplay is temporarily suspended. |
| **Match Finished** | When the shootout concludes and the Match Result is presented. |
| **Saving Progress** | When progression is being recorded (e.g., after a match, on achievement unlock, on settings change). |
| **Error State** | When an action cannot be completed (e.g., a save cannot be written or a save cannot be read). |
| **Exit Confirmation** | When the user requests to quit and confirmation is pending. |

---

## 7. Decision Points

| Decision | Impact on Flow |
|---|---|
| **Choose Game Mode** | Determines whether the user enters Practice, Tournament, or Career, and which setup screens follow. |
| **Choose Team** | Sets the team for the match or series; required before proceeding in applicable modes. |
| **Choose Difficulty** | Sets the challenge level; required before a match begins. |
| **Pause vs. Continue** | Pausing suspends the match and opens in-match options; continuing keeps the user in gameplay. |
| **Retry Match** | Restarts the current match instead of advancing or returning to the menu. |
| **Continue Series** | In Tournament/Career, advances to the next round or match rather than exiting. |
| **Save Progress** | Confirms whether progression and settings changes are retained. |
| **Abandon Tournament / Quit Match** | Leaves the current series and returns toward the menu; requires confirmation. |
| **Exit Game** | Ends the session; requires confirmation. |

---

## 8. Error & Edge Case Flows

These describe the **expected user flow**, not implementation.

- **No save file exists:** When the user selects Continue Career (or similar), the application informs them that no saved progress exists and offers to start a new career instead.
- **Corrupted save file:** The application informs the user that existing progress could not be loaded and offers a safe path forward (e.g., start fresh), without leaving the user stuck.
- **User cancels exit:** Selecting Cancel on the Exit Confirmation returns the user to the Main Menu with no change.
- **User pauses during replay:** The replay is interrupted, the Pause Menu is presented, and on Resume the user returns to active gameplay.
- **User attempts to quit during a tournament:** A confirmation dialog warns that tournament progress may be lost; on confirm, the user returns to the Main Menu; on cancel, they remain in the tournament.
- **Invalid settings:** The user is prevented from saving an invalid configuration and is prompted to correct it before continuing.
- **Failed save operation:** The user is notified that progress could not be saved and is offered the option to retry or continue, ensuring they are never silently blocked.

---

## 9. Persistence Flow

Progress should be saved at meaningful, predictable moments. (File formats and storage mechanisms are out of scope.)

- **End of match** — match outcomes and updated statistics are recorded.
- **Achievement unlocked** — newly earned achievements are recorded.
- **Settings changed** — preference changes are saved when the user confirms them.
- **Tournament completed** — final tournament outcomes and rewards are recorded.
- **Career progress updated** — career advancement is recorded as the player progresses.

Saving occurs in the background as part of these moments; the user should always be able to trust that their progress is retained.

---

## 10. UX Principles

The flow is designed to uphold the following principles throughout:

- **Minimal clicks** — the path from launch to gameplay is short and direct.
- **Clear navigation** — every screen makes the next and previous steps obvious.
- **No dead ends** — every screen offers a way forward and a way back.
- **Consistent back navigation** — Back behaves predictably everywhere.
- **Predictable screen transitions** — users always understand where an action leads.
- **Fast access to gameplay** — playing is never more than a few steps away.
- **Logical progression** — setup, play, result, and reward follow a natural order.

---

## 11. Out of Scope

This document intentionally excludes:

- UI design, layout, colors, and fonts.
- Wireframes and mockups.
- Technical implementation and programming logic.
- File structures, class design, and algorithms.

Those concerns belong in later design and engineering documents.

---

*End of document.*
