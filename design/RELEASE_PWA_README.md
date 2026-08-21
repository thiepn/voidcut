# VOIDCUT — Release / PWA Hardening

This phase repairs the packaging contract discovered during VD7 certification. It does not redesign VOIDCUT and does not change gameplay, save, replay, arena, Director or Daily-generation contracts.

## Packaging contract

The release root must contain:

- `index.html`
- `manifest.webmanifest`
- `sw.js`
- `icon.svg`
- `icon-192.png`
- `icon-512.png`
- `icon-maskable-512.png`
- `design/voidcut-design-system.css`
- `design/voidcut-design-system.js`

`index.html` already contains the manifest/icon references and service-worker registration used by the app's existing Install and Update Ready controls.

## Manifest

The manifest is scope-relative so the same package works from a repository subpath such as GitHub Pages or from a custom domain root:

- `id`: `./`
- `start_url`: `./`
- `scope`: `./`
- display: `standalone`
- orientation: `any`
- Paper background/theme color: `#E9E4D8`
- 192×192 any-purpose PNG
- 512×512 any-purpose PNG
- 512×512 maskable PNG

## Service-worker strategy

Cache namespace: `voidcut-shell-*`

Current cache version: `6.0.0-pwa2`

`pwa2` is the post-release layout-hotfix shell revision. It refreshes the precached design-system CSS containing the gameplay Pause and Records navigation corrections; application build and persistence contracts remain 6.0.0 / save 16 / replay 8.

The worker precaches the complete runtime shell during `install`. Installation fails atomically if any required release asset is missing.

The worker deliberately does **not** call `skipWaiting()` during installation. A new worker remains waiting while an existing release controls the page. This preserves VOIDCUT's existing user-facing update flow:

1. registration detects a waiting worker;
2. the menu exposes **UPDATE READY**;
3. VOIDCUT persists the save before applying the update;
4. the app sends `{ type: 'SKIP_WAITING' }`;
5. the new worker activates and claims clients;
6. `controllerchange` reloads the game.

This prevents a release from being swapped silently during an active run.

### Atomic release rule

**Every deployment that changes any precached runtime asset must also change `VOIDCUT_CACHE_VERSION` in `sw.js`.**

A new cache version gives the installing worker its own complete shell. On activation, only obsolete caches whose names begin with `voidcut-shell-` are deleted. Unrelated origin caches are never purged.

For the next runtime-asset deployment, increment `6.0.0-pwa2` to a new revision such as `6.0.0-pwa3`.

## Fetch policy

- navigation: cached release shell first, network fallback only if the shell is unexpectedly absent;
- precached runtime assets: cache first;
- non-core or cross-origin requests: not intercepted by the release worker.

The policy intentionally favors release consistency over silent background mutation. The explicit update path is responsible for moving an installed client to a newer shell.

## Offline contract

After the first successful online installation and activation, VOIDCUT must launch and reload without network access using only its precached release shell. Save data remains in the existing local-storage persistence system and is outside the service-worker cache.

## Certification gates

Release/PWA certification must verify:

- every HTML-referenced package asset exists and returns successfully;
- manifest parses and contains valid scope/start URL/icon declarations;
- PNG dimensions are exactly 192×192 / 512×512 / 512×512;
- `sw.js` passes JavaScript syntax validation;
- the complete service-worker precache installs successfully;
- a controlled reload has an active service-worker controller;
- offline reload succeeds with no network access;
- all core shell assets exist in the release cache;
- an updated worker waits rather than replacing the active release immediately;
- `SKIP_WAITING` activates the update and removes only obsolete VOIDCUT caches;
- no unexpected browser console, page, or request failures occur;
- VD7's certified `index.html` remains unchanged unless a release defect specifically requires modification;
- any post-certification design-system CSS change receives a focused rendered regression pass before merge;
- release metadata remains build 6.0.0, save 16, replay 8, arena 2, director 6, daily 1.

## Compatibility boundary

This phase must not change deterministic simulation, scoring, balance, progression, Mastery, cosmetics, save schema, stored setting IDs, replay format/verification, import/export formats, arena generation, Director generation or Daily generation.
