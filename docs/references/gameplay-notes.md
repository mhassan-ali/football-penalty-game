# Reference — Gameplay Notes

| Field | Value |
|---|---|
| **Document Type** | Reference (supporting notes) |
| **Status** | Living reference |
| **Date** | 2026-06-27 |
| **Related** | `01_PRD.md`, `02_APP_FLOW.md` |

> Working notes on gameplay feel and intent. These elaborate on the PRD and App Flow and do not override them. They describe experience, not implementation.

---

## 1. Core Loop (Experience View)

A penalty shootout is a series of decisive duels. Each attempt is a small story: anticipation → decision → action → outcome → reaction. The loop should stay short and tense, inviting "one more match."

```
Set up shot/defense  →  Decide (aim/power or dive)  →  Resolve  →  React (celebrate/relief)  →  Next attempt
```

## 2. The Shooter Experience

- Aiming and power should feel **intentional and skillful**, not random.
- The window to decide should create **pressure** without feeling unfair.
- A clean goal should feel **powerful and satisfying**; a miss should feel like the player's call, not the game's fault.

## 3. The Goalkeeper Experience

- Defending should feel like **reading and reacting** to the shooter.
- A save should feel **dramatic and earned**.
- The keeper's intent should be **readable** so duels feel fair.

## 4. Difficulty Feel (Player Perspective)

| Level | Intended Feel |
|---|---|
| **Easy** | Forgiving and confidence-building; the player feels capable. |
| **Medium** | Balanced and engaging; success requires attention. |
| **Hard** | Demanding and tense; little margin for error, punishes predictability. |

*(Behavior is described by feel only; algorithms and tuning live in implementation, not here.)*

## 5. Tension & Pacing

- Maintain visible stakes (score, remaining attempts) to sustain tension.
- Let big moments breathe (goal/save reactions, replays) without slowing the loop overall.
- Keep downtime between attempts short to preserve momentum.

## 6. Reward & Replayability

- Wins, trophies, unlockables, statistics, and achievements should give clear reasons to return.
- Progress should feel **earned and visible**, never grindy.
- Each mode (Practice, Tournament, Career) offers a distinct reason to play.

## 7. Open Questions / To Tune Later

- Exact number of attempts per shootout and sudden-death handling.
- Whether a timer/pressure element is used and how it is communicated.
- Balance of aiming vs. power inputs for skill expression.
- Replay frequency and length.

*These notes should be revisited after early playtests of the vertical slice.*
