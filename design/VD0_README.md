# VOIDCUT VD0 — Visual Infrastructure

VD0 establishes the new visual-design foundation without changing gameplay, simulation, scoring, deterministic replays, progression, saves, or the v6 renderer.

## Included

- `voidcut-design-system.css` — semantic design tokens, six themes, type scale, spacing, geometry, physical surfaces, texture, controls, status patterns, responsive grid, reduced-motion/high-contrast behavior.
- `voidcut-design-system.js` — persistent theme/texture runtime, event API, icon factory, and a runtime token/contrast audit.
- `vd0-preview.html` — standalone specimen used to validate the foundation before VD1 renderer reconstruction.

## Canonical themes

1. Paper (default)
2. Carbon
3. Cobalt
4. Kelp
5. Plum
6. Mono

## Integration contract for VD1

Renderer/UI code must consume semantic `--vc-*` variables rather than direct color literals or legacy cyan/magenta variables. New components must use the prefixed `.vc-*` primitives or component-local styles built from these tokens.

Legacy v6 variables are intentionally not aliased to the new system in VD0. This prevents an intermediate recolor from being mistaken for the redesign and avoids making the old glow/glass visual language a dependency of v7.

## Runtime API

`window.VoidcutDesign` exposes:

- `themes`
- `applyTheme(id)`
- `cycleTheme(step)`
- `getTheme()`
- `setTextureMode(mode)`
- `getTextureMode()`
- `createIcon(name, options)`
- `audit()`

Theme event: `voidcut:themechange`

Texture event: `voidcut:texturechange`

## VD0 acceptance gates

- all six themes resolve the full semantic token set, including distinct background and surface ink roles;
- default text/background and text/surface contrast meet 4.5:1;
- no new glow, glassmorphism, cyan/magenta brand dependency, or large-radius component language;
- texture is static, seeded, subtle, and can be reduced/disabled;
- icon grammar is consistent and independent of color;
- reduced-motion and increased-contrast preferences have defined behavior;
- VD0 does not mutate v6 gameplay behavior.

Next phase: **VD1 — Core Renderer Reconstruction**.
