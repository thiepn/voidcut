# VOIDCUT Release / PWA Hardening Status

**COMPLETE — PWA RELEASE CERTIFICATION PASS**

The automated release gate passed the static package, Chromium service-worker, installability/manifest, offline reload and explicit-update lifecycle checks.

Certified package behavior:

- all root manifest/icon/service-worker assets exist;
- PNG install icons are 192×192, 512×512 and 512×512 maskable;
- complete runtime shell precache installs successfully;
- a controlled reload has an activated service-worker controller;
- offline reload boots VOIDCUT from the release cache;
- a second worker revision installs into a separate cache and waits;
- `SKIP_WAITING` activates that revision and removes the obsolete VOIDCUT cache;
- unrelated cache namespaces are not targeted;
- the VD7-certified `index.html` and design-system CSS blobs are unchanged;
- release contracts remain build 6.0.0, save 16, replay 8, arena 2, director 6, daily 1.

Cache version certified: `6.0.0-pwa1`.
