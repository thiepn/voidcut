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
| VC-001 | CRITICAL | Replay verifier treats timestamps as not-before times, allowing stale/queued cuts to execute later with zero input delay. | F1 | FIXED — F1 PASS |
| VC-002 | CRITICAL | Ranked runs can be manually paused or lifecycle-paused without losing leaderboard eligibility. | F2 | FIXED — F2 PASS |
| VC-003 | CRITICAL | Main-loop frame-gap clamping can create a slow-motion competitive advantage under throttling/stalls. | F3 | FIXED — F3 PASS |
| VC-004 | HIGH | Replay verifier lacks a hard maximum simulation duration/step budget and can be forced into excessive CPU work. | F4 | FIXED — F4 PASS |
| VC-005 | HIGH | Global replay retrieval lowercases hashes but validates with an uppercase-only hexadecimal regex. | F5 | FIXED — F5 PASS |
| VC-006 | HIGH | Anonymous rate-limit identity uses IP + attacker-controlled User-Agent and is trivially splittable. | F6 | FIXED — F6 PASS |
| VC-007 | HIGH | Turnstile backend enforcement is implemented without matching client token acquisition/submission. | F7 | FIXED — F7 PASS |
| VC-008 | MEDIUM | PLAY can consume no leaderboard ticket if asynchronous prefetch has not completed, silently starting an unranked run. | F8 | FIXED — F8 PASS |
| VC-009 | MEDIUM | Only one in-memory pending leaderboard submission is retained; later runs/reloads/network failure can lose a valid submission. | F9 | FIXED — F9 PASS |
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


## F1 implementation record — strict replay input timing

- Current replay v9 input timestamps are now treated as exact deterministic simulation-time input starts within `REPLAY_TIME_EPS = 1e-6`, not as `not-before` queue times.
- A v9 input that becomes older than the current simulation time is rejected as `stale-input`; it is never deferred until the active cut finishes.
- v9 event timestamps must be strictly increasing, so identical input-start timestamps are invalid before simulation.
- v9 events later than `deathTime + REPLAY_TIME_EPS` are invalid.
- Deterministic verification now requires every replay event to have been consumed when death occurs, preventing ignored post-death inputs from verifying.
- Replay playback and replay seeking use the same timing classifier as local/server analysis and fail closed on stale timing.
- Replay v1–v8 retain the legacy `not-before` timing behavior for local backward-compatible viewing.
- Built-in stress diagnostics now cover strict due/stale/future classification, legacy timing compatibility, and duplicate v9 timestamp rejection.
- The generated Cloudflare verifier must be rebuilt from this source before F1 is closed.

F1 changes are limited to replay timing integrity and regression coverage; gameplay balance, visuals, game modes and save schema remain unchanged.

### F1 verification evidence

- Inline runtime JavaScript parses successfully after hardening.
- Source-level timing regression tests pass for v9 due/stale/future classification.
- Duplicate/effectively-duplicate v9 timestamps are rejected.
- Legacy v8 duplicate timestamp validation remains backward-compatible.
- Generated server verifier contains the same strict timing helper, stale-input rejection and all-events-consumed verification requirement.
- Generated verifier and Worker source pass Node syntax checks.

**F1 disposition: PASS. VC-001 closed.**

## F2 implementation record — ranked pause invalidation

- Global leaderboard eligibility is now fail-closed on the first pause of a ticketed standard PLAY run.
- Manual pause, keyboard pause, pause-button use, browser/app suspension, tab visibility loss, pagehide/freeze, and significant display-change pauses all converge on the same invalidation path.
- Invalidation immediately discards the active leaderboard ticket, so the completed replay cannot enter the submission queue.
- The run remains playable locally after invalidation; local records, replay export, progression and retry behavior are preserved.
- Tutorial, challenge and replay pause behavior is unchanged because they never own a global leaderboard ticket.
- Each new standard run resets the invalidation state and may use a fresh prefetched ticket normally.
- The pause sheet and final result explicitly disclose when the current run became unranked.

F2 changes are limited to leaderboard eligibility around pause/lifecycle interruption. Simulation timing hardening remains reserved for F3.

### F2 verification evidence

- Inline runtime JavaScript parses successfully after ranked-pause hardening.
- Manual pause invalidates the active global leaderboard ticket before pause state is committed.
- Lifecycle suspension routes through the same invalidation path with an explicit APP SUSPENDED reason.
- Significant display-change pause routes through the same invalidation path.
- Tutorial/non-play/already-unranked cases do not destroy unrelated tickets.
- New runs reset invalidation state and preserve normal fresh-ticket behavior.
- Result and pause UI expose the unranked state.
- F1 replay timestamp regression remains green.

**F2 disposition: PASS. VC-002 closed.**

## F3 implementation record — ranked wall-clock integrity

- Ranked standard PLAY now maintains an explicit runtime timing-integrity ledger separate from deterministic simulation state.
- Active-play frame wall time is compared against the bounded simulation delta; discarded wall time is accumulated rather than silently ignored.
- Any active-play frame gap greater than 200 ms immediately invalidates global leaderboard eligibility as `FRAME STALL`.
- Cumulative discarded active-play wall time of 250 ms or more invalidates eligibility as `TIMING DRIFT`, preventing repeated smaller throttling gaps from accumulating a meaningful reaction-time advantage.
- Any ranked main-loop catch-up step-cap hit invalidates eligibility as `CATCH-UP LIMIT`.
- Lifecycle and viewport timing resets debit unsimulated wall time plus pending accumulator time into the same discarded-time budget before clocks are reset.
- Significant display changes retain the F2 pause invalidation path; insignificant repeated viewport resets can no longer erase simulation time indefinitely without eventually becoming unranked.
- Intentional chamber transitions, paused runs, tutorial/challenge/replay states and already-unranked runs are excluded from ranked timing accounting.
- Timing invalidation discards the active leaderboard ticket but leaves the run fully playable and recordable locally.

F3 does not alter simulation speed, physics, scoring, replay format or save schema. It only determines whether a locally playable standard run remains eligible for global submission.

### F3 verification evidence

- Inline runtime JavaScript parses successfully after wall-clock integrity hardening.
- Smooth 60 FPS-equivalent ranked timing remains eligible with zero discarded-time debit.
- A moderate isolated frame stutter remains inside tolerance.
- Any active-play frame gap over 200 ms invalidates ranking as FRAME STALL.
- Repeated smaller clamped gaps invalidate once cumulative discarded wall time reaches 250 ms.
- Any main-loop catch-up step-cap hit invalidates ranking as CATCH-UP LIMIT.
- Lifecycle and viewport timing resets debit unsimulated wall time and accumulator residue before reset.
- Transition and paused states are excluded from active-play timing enforcement.
- F1 replay timestamp and F2 ranked-pause regressions remain green.

**F3 disposition: PASS. VC-003 closed.**

## F4 implementation record — replay verifier resource ceilings

- Current competitive replay verification now has explicit pre-simulation ceilings: 30 minutes (`1800 s`), 12,000 input events, and 216,100 deterministic simulation steps.
- The step counter is independent of replay `deathTime`, so verifier termination no longer depends solely on attacker-controlled duration fields or simulation-clock progress.
- Browser/local replay compatibility keeps the existing broader 50,000-event / 12 MB import envelope; the tighter ceilings apply only when `analyzeReplayData(..., true)` is used by the generated global verifier.
- The generated verifier now explicitly invokes competitive analyzer mode.
- The leaderboard Worker rejects over-limit event counts/durations before deterministic verification and before replay hashing/storage.
- Maximum leaderboard replay request size is reduced from 12.5 MB to 2.5 MB.
- Durable Object replay ingestion now reads the request stream incrementally with a byte counter and cancels once the limit is crossed, including when `Content-Length` is missing or false.
- Existing edge `Content-Length` rejection remains as an earlier fast path.

F4 does not change physics, scoring, save schema, replay version, local replay playback rules, or gameplay balance.

### F4 verification evidence

- Inline runtime JavaScript parses after resource-budget hardening.
- Competitive preflight accepts the exact 30-minute / 12,000-event boundary and rejects values above either ceiling.
- Local/legacy replay validation retains its broader compatibility envelope.
- Competitive analyzer contains an independent 216,100-step fail-safe checked before each deterministic simulation update.
- Leaderboard request ingestion is capped at 2.5 MB and chunked bodies are byte-counted/cancelled while streaming.
- Worker structural resource preflight runs before deterministic verification.
- Generated server verifier explicitly invokes competitive analyzer mode and contains the same event, duration and step ceilings.
- Generated verifier and Worker source pass Node syntax checks.
- F1, F2 and F3 permanent regressions remain green.

**F4 disposition: PASS. VC-004 closed.**

## F5 implementation record — canonical replay hash retrieval

- Global replay IDs are now normalized exactly once to lowercase before validation and lookup.
- The canonical validator accepts only 64 hexadecimal characters after normalization.
- Both lowercase and uppercase request forms resolve to the same canonical lowercase SHA-256 identifier.
- D1 `best_replay_hash` lookup and R2 `verified/<hash>.json` lookup now use the same canonical lowercase value.
- This matches the existing `sha256()` implementation, which emits lowercase hexadecimal, and the route layer, which already lowercases `/replay/<hash>` path values.
- Invalid length/non-hex replay IDs still fail with `invalid-replay`.

F5 changes only global replay retrieval normalization; replay generation, verification, scoring, storage format, save schema and gameplay are unchanged.

### F5 verification evidence

- Lowercase 64-character SHA-256 replay IDs validate unchanged.
- Uppercase and mixed-case request forms canonicalize to the same lowercase identifier.
- Invalid-length and non-hex replay IDs remain rejected.
- D1 owner lookup and R2 replay-object lookup both use the canonical lowercase identifier.
- The route-level lowercase normalization and lowercase `sha256()` output are consistent with the retrieval helper.
- The obsolete uppercase-only validator is absent.
- Worker syntax and F4 replay-resource regression remain green.

**F5 disposition: PASS. VC-005 closed.**

## F6 implementation record — stable anonymous rate-limit identity

- Anonymous profile-creation and run-ticket rate limits now key only on Cloudflare's server-provided `CF-Connecting-IP`; attacker-controlled `User-Agent` is no longer part of rate-limit identity.
- The key is namespaced as `ip:<address>` so its meaning is explicit and cannot be confused with authenticated player/token identities.
- Requests without a `CF-Connecting-IP` use the stable fail-closed bucket `ip:unknown` rather than a caller-controlled fallback header.
- Rotating, randomizing or omitting `User-Agent` therefore cannot create additional anonymous profile/run rate-limit buckets.
- Authenticated run tickets continue to use the authenticated player ID, and score submission throttling continues to use the SHA-256 of the bearer token; F6 does not weaken authenticated throttling.
- Existing Cloudflare rate-limit quotas and namespaces remain unchanged.

F6 changes only anonymous rate-limit identity construction; authentication tokens, leaderboard rules, replay verification, scoring, storage, save schema and gameplay are unchanged.

### F6 verification evidence

- Two requests from the same `CF-Connecting-IP` produce the same anonymous limiter key even when `User-Agent` is changed, randomized or omitted.
- Different trusted client IPs produce distinct anonymous limiter keys.
- Missing trusted IP falls into the stable `ip:unknown` fail-closed bucket.
- The anonymous key does not consult `User-Agent`, `X-Forwarded-For`, `X-Real-IP`, or other caller-controlled identity headers.
- Profile creation and unauthenticated run-ticket issuance both use the hardened anonymous key.
- Authenticated run-ticket and bearer-token submission throttling remain unchanged.
- Cloudflare limiter namespaces, quotas and periods remain unchanged.
- Worker syntax, F4 replay-resource regression and F5 replay-hash regression remain green.

**F6 disposition: PASS. VC-006 closed.**

## F7 implementation record — remove incomplete Turnstile contract

- The dormant Cloudflare Turnstile verification helper and conditional profile-creation gate have been removed from the leaderboard Worker.
- The shipped client never loaded Turnstile, had no site key/widget/token acquisition path, and submitted profile creation as `{name}` only; retaining a backend-only optional requirement could therefore make legitimate profile creation fail whenever deployment configuration enabled it.
- F7 deliberately chooses removal rather than adding a new third-party runtime dependency, site-key contract and secret-management requirement late in the hardening cycle.
- Anonymous abuse protection remains provided by F6's server-controlled `CF-Connecting-IP` rate-limit identity and the existing Cloudflare PROFILE/RUN limiter bindings.
- Authenticated submission throttling, replay verification and leaderboard identity tokens are unchanged.
- No client UI, gameplay, scoring, save schema, replay format or release metadata changed.

If Turnstile is introduced in a future release, it must be implemented as an explicit end-to-end client/server feature with deployment configuration and regression coverage rather than as a dormant backend switch.

### F7 verification evidence

- Worker contains no dormant Turnstile helper, environment switch, secret lookup, token field, siteverify URL or `human-check-failed` response path.
- Shipped client and source client remain consistent: profile creation sends only the public name and contains no partial Turnstile widget/token integration.
- Profile creation still enforces F6 anonymous network rate limiting, name validation, opaque token creation/hash storage and D1 persistence.
- PROFILE/RUN/SUBMIT Cloudflare limiter quotas remain unchanged.
- Worker syntax and permanent F1-F6 regressions remain green.

**F7 disposition: PASS. VC-007 closed.**

## F8 implementation record — synchronized ranked run start

- Standard PLAY no longer calls `takeLeaderboardTicket()` synchronously while a ticket prefetch may still be in flight.
- Ranked start acquisition first consumes an already-ready ticket; otherwise it awaits the existing/new ticket request within a bounded 2,000 ms start budget.
- A successful acquisition uses the server-issued ticket seed for the run exactly as before.
- If the ticket request settles without a usable ticket, the run starts locally with explicit `LEADERBOARD UNAVAILABLE` status.
- If the ranked-start budget expires first, the run starts locally with explicit `LEADERBOARD TIMEOUT` status; the still-running prefetch may only prepare a ticket for a later run.
- While acquisition is pending the lifecycle state is `starting`, preventing cuts/pause/key-repeat starts from treating the not-yet-started run as active gameplay.
- Repeated standard start attempts share one `rankedStartPromise`, so double-click/Space cannot create parallel ticket acquisitions or multiple runs.
- Before launch, the async continuation verifies the state is still `starting`; navigation away during the bounded wait cancels that pending launch instead of unexpectedly starting a run later.
- Mouse PLAY, keyboard Space, standard retry/restart and post-tutorial standard start all converge on the same synchronized `start()` path.
- Challenge starts bypass ranked-ticket acquisition and remain unchanged.
- The source client fragment and shipped inline leaderboard runtime now share the same acquisition helper and 2,000 ms contract.

F8 changes only standard-run ticket acquisition/start synchronization and explicit ranked/local status. Physics, scoring, replay format, save schema, ticket TTL, server seed generation and leaderboard verification are unchanged.

### F8 verification evidence

- A ready valid ticket is consumed immediately without issuing another ticket request.
- If no ready ticket exists, standard PLAY awaits the existing/new prefetch rather than synchronously choosing a local seed.
- A ticket that resolves inside the 2,000 ms start budget is consumed and its server seed remains authoritative for the ranked run.
- A settled request with no ticket produces explicit `LEADERBOARD UNAVAILABLE` local-run status.
- A ticket arriving after the bounded start budget cannot attach to the already-starting run; that run becomes explicitly local with `LEADERBOARD TIMEOUT`, while the late ticket may be reused only by a later run.
- Repeated start attempts share one pending start promise, and navigation away prevents the async continuation from launching unexpectedly.
- The F2 explicit new-run invalidation reset remains intact before any F8 local-start reason is applied.
- Standard mouse, keyboard, retry/restart and post-tutorial starts converge on the synchronized path; challenge starts remain outside global-ticket acquisition.
- Inline runtime parses successfully, source-client and shipped acquisition helpers match, and F1-F7 permanent regressions remain green.

**F8 disposition: PASS. VC-008 closed.**

## F9 implementation record — persistent multi-entry leaderboard submission queue

- The single volatile `pendingLeaderboardSubmission` slot has been removed.
- Ranked submissions are now enqueued under the dedicated `voidcut.leaderboard.submissions.v1` local-storage key before any network submission attempt.
- The queue retains up to 16 distinct ticket/replay entries and never evicts an existing valid entry merely to make room for a later run; a full queue is surfaced explicitly as `GLOBAL QUEUE FULL`.
- Queue writes are read back immediately. If persistent storage is unavailable, the entry remains in the current in-memory queue as a best-effort volatile fallback and the UI surfaces `GLOBAL QUEUE STORAGE FAILED`.
- Queue loading rejects malformed entries, de-duplicates ticket IDs and prunes tickets whose server expiry has passed. Corrupt JSON is discarded rather than preventing startup.
- Submissions drain sequentially so multiple completed runs cannot overwrite each other or create parallel submission storms.
- Success removes only the successfully handled ticket. The server's verified-ticket idempotence makes an accidental retry after a failed local queue cleanup safe.
- HTTP 400/403/404/409/410/413/422 responses are treated as terminal for that ticket and remove only that entry; the queue then continues.
- HTTP 401 preserves the queue, clears the invalid local identity and waits for profile recovery.
- HTTP 429, network failures and 5xx responses preserve the queue and schedule a bounded 15-second retry while online.
- Browser `online` and normal menu entry both trigger queue draining, so reload/offline recovery resumes automatically once a valid identity and connectivity are present.
- Creating a leaderboard profile drains every queued run rather than submitting only the most recent one.
- No Worker, replay verifier, ticket TTL, scoring, physics, save schema or leaderboard ordering changed in F9.

### F9 verification evidence

- Two distinct ranked ticket/replay pairs coexist in persistent storage without overwrite, and a simulated reload restores both.
- Duplicate ticket IDs replace their own payload rather than duplicating or removing other queue entries.
- Expired and malformed entries are pruned safely; corrupt queue JSON fails closed without preventing startup.
- The 16-entry bound refuses overflow without evicting existing valid queued runs.
- Persistent-write failure is surfaced while retaining the new entry in the current session for best-effort immediate submission.
- Every ranked submission is enqueued before a network drain begins.
- Queue draining is single-flight and sequential across all queued entries.
- Success and terminal rejection remove only the handled ticket; 401 preserves queued work for identity recovery; 429/network/5xx preserve queued work for retry.
- Online recovery, menu entry and profile creation all resume draining.
- The obsolete `pendingLeaderboardSubmission` and direct `submitLeaderboardRun` paths are absent.
- Inline runtime parses successfully, Worker syntax remains green, and permanent F1-F8 regressions remain green.

**F9 disposition: PASS. VC-009 closed.**
