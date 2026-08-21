# VOIDCUT v6.0.0 — Final Release Integration & Deployment Certification

Status: **CERTIFICATION IN PROGRESS**

This is the final integration gate for the complete VD0 → VD7 → Release/PWA reconstruction. The release-candidate branch is `chatgpt/v6-final-release-candidate` and integrates the complete stack directly against `main`.

## Release-candidate goals

- prove every phase head is contained in one release history;
- preserve build 6.0.0 / save 16 / replay 8 / arena 2 / director 6 / daily 1;
- reject conflict markers, missing runtime assets, duplicate IDs and packaging regressions;
- verify fresh boot and service-worker-controlled reload;
- verify representative legacy raw saves migrate to schema 16 without losing key player data;
- rerun VOIDCUT's deterministic release stress audit;
- certify offline reload and explicit waiting-worker update behavior;
- certify service-worker unregister/reinstall behavior;
- smoke-test Chromium, Firefox and WebKit engine boots at desktop/mobile sizes;
- certify both custom-domain-root (`/`) and GitHub-Pages-style project-path (`/voidcut/`) hosting semantics;
- reject same-origin HTTP 4xx/5xx and request failures;
- preserve the already certified VD7 product and PWA package.

## Release topology

The RC branch is created directly from the certified PWA-hardening head. The stacked development PRs remain historical review layers; this RC PR is the single proposed integration into `main`.

No production merge or deployment is performed by this certification phase without explicit authorization.
