# VOIDCUT VD7 — Theme Suite & Responsive Certification

VD7 is the whole-product certification layer after VD0–VD6. It does not redesign individual screens. It proves that the reconstructed CUTFORM product behaves as one visual system across themes, viewports, interaction modes and utility states.

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

Small semantic text must meet a 4.5:1 contrast target against its intended background. VD7 specifically certifies:

- background ink / background
- background muted ink / background
- primary ink / surface
- secondary ink / surface
- muted ink / surface
- on-accent ink / accent

Mono must remain mechanically distinguishable through shape/pattern as well as color.

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

Each target must be checked for horizontal overflow, clipped text, primary-action clarity, arena dominance, safe-area behavior and interactive control size. Content-heavy archive/manual screens may scroll vertically; accidental horizontal scrolling is never acceptable.

## Responsive rules

- minimum interactive target: 44 CSS px on touch-oriented utility controls
- no critical control may depend on hover
- phone layouts may scroll vertically, but key navigation must remain legible and reachable
- desktop layouts must read as intentional desktop compositions rather than centered phone frames
- short landscape receives a dedicated compact composition instead of blind scaling
- ultrawide layouts cap content density and preserve negative space

## Theme ownership

Final active product surfaces must resolve through semantic CUTFORM tokens. Legacy v5 cyan/magenta variables may remain internally for historical code compatibility, but VD7 must prevent them from owning visible product color.

Browser chrome is synchronized to the current `--vc-bg` token through the existing `theme-color` meta tag.

## Compatibility boundary

VD7 must not change:

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

Release contracts remain build 6.0.0, save 16, replay 8, arena 2, director 6, daily 1.

## Runtime certification

VD7 exposes `window.VoidcutCertification` with:

- `audit()` — current runtime/theme/responsive audit
- `auditThemes()` — semantic contrast results across all six themes
- `viewports` — the canonical certification matrix
- `themes` — the canonical theme order

The final browser certification pass must exercise the menu, product panels, Settings, Diagnostics, Pause, Result and Replay utility layouts across the target matrix.
