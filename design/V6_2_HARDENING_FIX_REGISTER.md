# VOIDCUT v6.2 Hardening — Fix Register

Status: **F0 BASELINE FROZEN — FIX CYCLE OPEN**

Created: 2026-08-26

## Frozen production baseline

- Repository: `thiepn/voidcut`
- Production branch at freeze: `main`
- Frozen commit: `39f52e0dd036896e38fbe886ae9b3f36e507cbf5`
- Frozen commit message: `Hard-remove intrusive screen-cut popup`
- Immutable archive reference: `archive/v6.1.0-pre-hardening-2026-08-26`
- Hardening work branch: `fix/v6.2-hardening`

### Runtime contracts at freeze

- Build: `6.1.0`
- Release channel: `stable`
- Save schema: `17`
- Replay version: `9`
- Arena generation: `2`
- Director generation: `6`
- Service-worker cache revision: `6.1.0-pwa4`

## Fix-cycle invariants

Until final certification:

1. No gameplay-balance changes.
2. No visual redesign.
3. No new game modes.
4. No Daily system or other recurring engagement system.
5. Preserve existing saves unless a migration is explicitly required and tested.
6. Preserve deterministic replay compatibility for supported legacy local replays unless a security requirement makes rejection necessary.
7. Global competitive integrity takes priority over retaining replay-v9 eligibility.
8. Every bug below must receive an automated regression test where technically practical.
9. `main` is not the working branch for this hardening cycle.
10. A successful deployment is not equivalent to release certification.

## Severity definitions

- **CRITICAL** — breaks competitive integrity or enables meaningful exploitation.
- **HIGH** — serious backend/PWA/reliability defect or security weakness.
- **MEDIUM** — reproducible correctness/reliability problem without immediate catastrophic impact.
- **LOW** — cleanup, consistency or edge-case issue that should still be corrected before certification when practical.

## Confirmed defect register

| ID | Severity | Defect | Planned phase | Status |
|---|---|---|---|---|
| VC-001 | CRITICAL | Replay verifier treats timestamps as not-before times, allowing stale/queued cuts to execute later with zero input delay. | F1 | OPEN |
| VC-002 | CRITICAL | Ranked runs can be manually paused or lifecycle-paused without losing leaderboard eligibility. | F2 | OPEN |
| VC-003 | CRITICAL | Main-loop frame-gap clamping can create a slow-motion competitive advantage under throttling/stalls. | F3 | OPEN |
| VC-004 | HIGH | Replay verifier lacks a hard maximum simulation duration/step budget and can be forced into excessive CPU work. | F4 | OPEN |
| VC-005 | HIGH | Global replay retrieval lowercases hashes but validates with an uppercase-only hexadecimal regex. | F5 | OPEN |
| VC-006 | HIGH | Anonymous rate-limit identity uses IP + attacker-controlled User-Agent and is trivially splittable. | F6 | OPEN |
| VC-007 | HIGH | Turnstile backend enforcement is implemented without matching client token acquisition/submission. | F7 | OPEN |
| VC-008 | MEDIUM | PLAY can consume no leaderboard ticket if asynchronous prefetch has not completed, silently starting an unranked run. | F8 | OPEN |
| VC-009 | MEDIUM | Only one in-memory pending leaderboard submission is retained; later runs/reloads/network failure can lose a valid submission. | F9 | OPEN |
| VC-010 | MEDIUM | Profile creation ignores failure to persist/read back local leaderboard identity, potentially orphaning the username/token relationship. | F10 | OPEN |
| VC-011 | MEDIUM | Local best-replay selection does not use the same score/chamber/time ordering as the global leaderboard. | F11 | OPEN |
| VC-012 | LOW | Exact-tie self-rank calculation omits the final player-ID tie-break used by leaderboard ordering. | F11 | OPEN |
| VC-013 | MEDIUM | Expired/rejected/used run tickets have no retention cleanup and accumulate indefinitely. | F12 | OPEN |
| VC-014 | LOW | Concurrent personal-best updates can leave obsolete/orphaned R2 replay objects. | F12 | OPEN |
| VC-015 | MEDIUM | Top-level Worker route try/catch does not await async route handlers consistently, weakening controlled error handling. | F13 | OPEN |
| VC-016 | HIGH | Service worker can cache an arbitrary successful same-scope navigation response under the canonical `index.html` shell key. | F14 | OPEN |
| VC-017 | MEDIUM | `skipWaiting()` automatic activation conflicts with UI logic that expects a waiting service worker for manual update activation. | F15 | OPEN |
| VC-018 | MEDIUM | Cache freshness for core design assets relies on manually changing the SW cache revision; mixed old/new assets are possible after an incomplete release update. | F16 | OPEN |
| VC-019 | MEDIUM | Cache-write failures can interfere with otherwise successful network responses instead of degrading gracefully. | F16 | OPEN |
| VC-020 | MEDIUM | `visualViewport` resize/scroll handling cancels gestures and resets timing before determining whether the change is significant. | F17 | OPEN |
| VC-021 | MEDIUM | Tutorial initialization partially mutates the current simulation instead of fully resetting generation/scoring/briefing state. | F18 | OPEN |
| VC-022 | LOW | Cosmetic unlock logic contains unreachable/conflicting branches for IDs already returned as always unlocked. | F19 | OPEN |
| VC-023 | LOW | Obsolete `.vc-screen-cut` hide rule remains even though the popup DOM/function/calls were removed. | F19 | OPEN |
| VC-024 | MEDIUM | Built-in diagnostics do not exercise live leaderboard API/replay retrieval, ranked timing integrity, or full SW update behavior. | F20 | OPEN |
| VC-025 | HIGH | Current v6.1/save17/replay9 code has not been run through the old full cross-browser/PWA certification suite. | F21 | OPEN |
| VC-026 | MEDIUM | Existing release-certification documents describe v6.0/save16/replay8 and stale Daily/PWA behavior. | F27 | OPEN |
| VC-027 | LOW | Leaderboard identity is outside the normal full-save export/import path; profile ownership is not portable/recoverable through the current backup flow. | F10/F24 | OPEN |

## Validation / release phases

The following phases are gates rather than single defects and remain mandatory:

| Phase | Gate | Status |
|---|---|---|
| F20 | Expand internal regression diagnostics | NOT STARTED |
| F21 | Restore automated cross-browser release suite for current contracts | NOT STARTED |
| F22 | Adversarial leaderboard / anti-cheat test suite | NOT STARTED |
| F23 | Destructive PWA lifecycle testing | NOT STARTED |
| F24 | Save migration, corruption and recovery audit | NOT STARTED |
| F25 | Manual desktop/mobile UX regression pass | NOT STARTED |
| F26 | Fresh final release audit | NOT STARTED |
| F27 | Final version/replay contract and documentation update | NOT STARTED |
| F28 | Controlled production deployment | NOT STARTED |
| F29 | Post-deployment production verification | NOT STARTED |

## Planned phase order

`F0 → F1 → F2 → F3 → F4 → F5 → F6 → F7 → F8 → F9 → F10 → F11 → F12 → F13 → F14 → F15 → F16 → F17 → F18 → F19 → F20 → F21 → F22 → F23 → F24 → F25 → F26 → F27 → F28 → F29`

## F0 exit criteria

- [x] Current `main` SHA independently verified.
- [x] Pre-hardening archive reference created from that exact SHA.
- [x] Dedicated hardening branch created from that exact SHA.
- [x] Current version/save/replay/arena/director contracts recorded.
- [x] Confirmed audit findings assigned stable IDs and fix phases.
- [x] Scope restrictions recorded.
- [x] No gameplay, balance, visual or runtime code changed in F0.

**F0 disposition: PASS. Proceed to F1 only on `fix/v6.2-hardening`.**
