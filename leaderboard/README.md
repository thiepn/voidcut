# VOIDCUT Global Leaderboard

Backend for VOIDCUT v6.1 global competition.

- `POST /run/start` issues a server seed and single-run ticket.
- `POST /profile/create` creates a lightweight name + device token identity; no email/password.
- `POST /run/submit/:ticketId` sends the completed replay to a per-ticket Durable Object.
- The Durable Object re-simulates replay v9 with verifier code extracted from the shipping game source.
- D1 stores identities, tickets and personal-best metadata.
- R2 stores only replay data needed by current leaderboard personal bests.
- `GET /leaderboard` returns the global Top 100 and optional caller position.
- `GET /replay/:hash` serves a verified leaderboard replay for spectating.

Normal game play does not depend on this service. If a ticket cannot be prefetched, VOIDCUT starts an ordinary unranked offline-capable run.

Turnstile support is dormant unless `TURNSTILE_REQUIRED=1` and `TURNSTILE_SECRET` are explicitly configured.
