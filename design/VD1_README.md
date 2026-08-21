# VD1 — Core Renderer Reconstruction

VD1 is the first visible phase of the CUTFORM redesign. It consumes the semantic visual infrastructure established in VD0 and replaces the active canvas playfield renderer without changing the deterministic game simulation.

## Renderer ownership moved in VD1

- gameplay backdrop -> solid substrate + static registration marks
- arena regions -> physical graphic panels with hard offset contact shadows
- cleared space -> exposed substrate instead of luminous void treatment
- cores -> flat physical discs with archetype glyphs and no aura field
- cuts -> scored substrate seams with square anchors and danger ink
- permanent dividers -> structural seams with fixed registration anchors
- collapse feedback -> physical panel lift, shear, fracture, or implosion
- trails -> restrained ink motion marks rather than light trails
- impact/ring/spark feedback -> flat graphic marks with no bloom ownership
- arena border/progress -> hard rule + accent registration stripe
- chamber transition -> physical information card instead of luminous sweep

## Explicitly removed from renderer ownership

- animated Void World backdrop layers during play
- core light/aura fields
- cut laser spill and shadow bloom
- divider moving light pulses
- collapse glow fields and white-hot radial effects
- arena outline glow
- radial impact bloom and gameplay vignette

## Preserved exactly

VD1 does not alter simulation, collision geometry, cut resolution, scoring, balance, chamber generation, director rules, saves, replay serialization, replay verification, progression, mastery, or cosmetics unlock state.

Existing cosmetic IDs remain compatible. VD1 reinterprets their rendering through the CUTFORM language instead of removing or migrating save data.

## Theme integration

`index.html` now loads:

- `design/voidcut-design-system.css`
- `design/voidcut-design-system.js`

The canvas renderer resolves semantic `--vc-*` tokens at runtime. Theme changes therefore affect the active field without maintaining a second independent renderer palette.

## Runtime audit

VD1 exposes `window.VoidcutRenderer.audit()` with the active renderer version/theme and invariants including `physicalCuts`, `coreGlow: false`, and `animatedBackdrop: false`.

## Scope boundary

The gameplay HUD, menu, settings, results, modifier briefings, milestone presentation, and other product-shell UI still contain substantial v6 visual language. They are intentionally outside VD1 and should be reconstructed in later visual phases rather than mixed into this renderer migration.
