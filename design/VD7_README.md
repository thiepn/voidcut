# VOIDCUT VD7 — Theme Suite & Responsive Certification

VD7 is the whole-product certification layer after VD0–VD6. It does not redesign individual screens. It proves that the reconstructed CUTFORM product behaves as one visual system across themes, viewports, interaction modes and utility states.

## Status

**VD7 COMPLETE — FINAL VISUAL CERTIFICATION PASS**

Final browser certification executed **150 rendered checks** across the canonical viewport matrix. All VD7 visual, theme, responsive and interaction-size gates passed.

The final certification run reported:

- `VD7 visual checks: 150`
- `VD7 FINAL VISUAL CERTIFICATION PASS`
- 0 visual/responsive certification failures
- 10 repeated known packaging notices caused by the pre-existing missing `sw.js` registration target; this is explicitly outside VD7 and must be resolved during release/packaging hardening

Temporary migration scripts, repair workflows, trigger files and browser-certification harnesses were removed during closeout. The permanent VD7 diff is intentionally limited to:

- `index.html`
- `design/voidcut-design-system.css`
- `design/VD7_README.md`

## Scope

- certify all six CUTFORM themes: Paper, Carbon, Cobalt, Kelp, Plum, Mono
- certify semantic text contrast and focus visibility
- remove remaining active cyan/magenta presentation leakage through final semantic ownership
- synchronize browser theme-color with the active CUTFORM theme
- certify phone, tablet, desktop and ultrawide compositions
- harden short-landscape layouts
- enforce minimum touch-target sizes on utility controls
- audit horizontal overflow and text containment
- preserve every VD0–VD6 ownership contract

## Canonical theme order

1. Paper — canonical reference
2. Carbon
3. Cobalt
4. Kelp
5. Plum
6. Mono — high-legibility monochrome variant

The persisted `settings.colorTheme` IDs remain unchanged. VD6 continues to bridge them onto these six themes.

## Contrast gate

Small semantic text is certified to a **4.5:1 minimum contrast target** against its intended background for the tested semantic pairs:

- background ink / background
- background muted ink / background
- primary ink / surface
- secondary ink / surface
- muted ink / surface
- on-accent ink / accent

The certification pass found real contrast deficiencies in several theme tokens and corrected them at the semantic-token level rather than weakening the threshold or patching individual screens.

Mono remains mechanically distinguishable through shape/pattern as well as color.

## Viewport matrix

### Phones
- 360 × 640
- 390 × 844
- 412 × 915

### Tablets
- 768 × 1024
- 820 × 1180

### Desktop
- 1280 × 720
- 1440 × 900
- 1920 × 1080
- 2560 × 1440

### Ultrawide
- 3440 × 1440

The final browser pass found no horizontal product/screen overflow in the tested matrix. Content-heavy archive/manual screens may scroll vertically; accidental horizontal scrolling is not permitted.

## Responsive rules

- minimum interactive target: 44 CSS px on touch-oriented utility controls
- no critical control may depend on hover
- phone layouts may scroll vertically, but key navigation must remain legible and reachable
- desktop layouts must read as intentional desktop compositions rather than centered phone frames
- short landscape receives a dedicated compact composition instead of blind scaling
- ultrawide layouts cap content density and preserve negative space

Chromium measurement exposed older 42–43.6px controls during certification. Those controls were normalized above the 44px certification floor.

## Theme ownership

Final active product surfaces resolve through semantic CUTFORM tokens. Legacy v5 cyan/magenta variables may remain internally for historical code compatibility, but VD7 prevents them from owning visible computed product color.

The browser gate explicitly inspected computed styles and pseudo-elements for retired cyan/magenta values. The final run passed with no detected visible legacy-color leakage.

Browser chrome is synchronized to the current `--vc-bg` token through the existing `theme-color` meta tag.

## Runtime certification

VD7 exposes `window.VoidcutCertification` with:

- `audit()` — current runtime/theme/responsive audit
- `auditThemes()` — semantic contrast results across all six themes
- `viewports` — the canonical certification matrix
- `themes` — the canonical theme order
- theme-color synchronization
- visible touch-target inspection
- horizontal-overflow reporting
- release-contract reporting

## Compatibility boundary

VD7 did not change:

- simulation or collision logic
- scoring or balance
- Director behavior
- progression or Mastery logic
- cosmetic unlock rules
- save schema or persisted setting IDs
- replay format or deterministic verification
- import/export formats
- Daily generation
- arena generation
- diagnostic test definitions

Release contracts remain:

| Contract | Version |
| --- | ---: |
| Build | 6.0.0 |
| Save | 16 |
| Replay | 8 |
| Arena | 2 |
| Director | 6 |
| Daily | 1 |

## Known out-of-scope packaging defect

`index.html` currently attempts to register `./sw.js`, but the repository does not contain `sw.js`. Headless Chromium therefore reports one service-worker fetch 404 per tested viewport.

This defect predates VD7 and does not affect the visual certification result, but it means the current repository must **not** be treated as fully PWA/offline-package certified until the service-worker packaging contract is repaired or the registration is intentionally removed in a dedicated release-hardening phase.

## Closeout

VD7 is closed as a successful visual phase. The CUTFORM reconstruction is now certified as one themeable and responsive visual system across the tested product surfaces and viewport matrix. The next release-hardening work should address packaging/PWA integrity separately rather than reopening visual ownership.
