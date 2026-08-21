# VOIDCUT v6.0.0 — Final Release Integration & Deployment Certification

Status: **V6_RC_CERTIFIED — RELEASE / DEPLOYMENT PACKAGE READY**

VOIDCUT v6.0.0 has passed the final integration and deployment-readiness gate for the complete VD0 → VD7 → Release/PWA reconstruction.

Release-candidate branch: `chatgpt/v6-final-release-candidate`

Target branch: `main`

Authoritative certification workflow:
- Run ID: `32521256771`
- Run number: `16`
- Conclusion: **success**
- Certified commit: `11ea00af0f40363288debd891a58e56013df545f`

## Certified release contracts

- Build: `6.0.0`
- Save schema: `16`
- Replay schema: `8`
- Arena generation: `2`
- Director generation: `6`
- Daily generation: `1`

## Frozen product blobs

- `index.html`: `8a8d8f2c21145cf9a53172e6bb1a900eae97b170`
- `design/voidcut-design-system.css`: `29456237edb9fb2a3cefd30157bc5729a3ffed04`

These blobs are the certified VD7 product surfaces and must remain unchanged through release integration unless certification is rerun.

## Integration certification

The release candidate contains the complete certified development history:

VD0 → VD1 → VD2 → VD3 → VD4 → VD5 → VD6 → VD7 → Release/PWA hardening.

The final static gate verified:

- `main` is an ancestor of the release candidate;
- every certified phase/PWA head is contained in the release history;
- the frozen `index.html` and design-system CSS blobs match their certified SHAs;
- required runtime/PWA assets are present;
- no real Git conflict markers remain;
- no duplicate DOM IDs are present;
- inline game JavaScript parses successfully;
- design-system JavaScript parses successfully;
- service-worker JavaScript parses successfully;
- manifest and icon contracts are valid;
- service-worker precache assets are complete.

## Browser and responsive certification

The final cross-engine smoke suite passed for both root-hosted and project-path deployment forms:

- Chromium — desktop and mobile
- Firefox — desktop and mobile
- WebKit — desktop and mobile
- root deployment: `/`
- project deployment: `/voidcut/`

The browser gate also verifies:

- application boot and menu visibility;
- VD7 runtime/design certification availability;
- theme-suite runtime audit;
- touch-target certification;
- absence of horizontal overflow;
- same-origin HTTP/request failure detection;
- fatal page/console error detection.

Unsupported-browser notices for the optional `interactive-widget` viewport token are treated only as compatibility notices; other runtime errors remain certification failures.

## Save compatibility certification

Representative raw legacy saves migrated successfully to schema 16:

- schema `1 → 16`
- schema `8 → 16`
- schema `15 → 16`

The migration checks preserve representative player progress, records, settings and cosmetics while repairing the primary save into the current schema-16 envelope.

## PWA and deployment certification

Both root and `/voidcut/` deployment replicas passed the full PWA lifecycle:

- fresh online boot;
- service-worker registration and control;
- release-cache creation;
- manifest/installability checks where available;
- built-in deterministic release stress audit;
- system diagnostics;
- offline reload;
- waiting-worker update behavior;
- explicit `SKIP_WAITING` activation;
- `controllerchange` handoff;
- obsolete-cache cleanup;
- service-worker unregister;
- reinstall and re-control;
- preservation of the current save schema through the lifecycle.

## Release disposition

**Certified for merge/deployment preparation.**

This certification does not itself merge PR #10 or deploy production. PR #10 must remain draft and unmerged until explicit deployment authorization is given.

Physical-device Safari/iOS certification is outside this automated gate; WebKit coverage is engine-level browser certification.
