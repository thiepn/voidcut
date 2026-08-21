# VD5 — Cosmetics Reconstruction

VD5 replaces the remaining neon showroom with a CUTFORM material/specimen system while preserving the underlying cosmetic IDs, unlock rules, save schema, loadout storage and gameplay behavior.

## Presentation model

- `arena` is presented as **FIELD**
- `ball` is presented as **DISC**
- `trail` is presented as **TRACE**
- `cut` remains **CUT**
- `collapse` is presented as **REMOVAL**

Internal IDs remain unchanged for compatibility.

## Reconstructed surfaces

- header / VOIDCUT cosmetics identity
- live full-loadout specimen
- field-material representation
- disc-construction representation
- trace representation
- cut representation
- removal representation
- saved loadout rack
- category rail
- individual specimen cards
- lock / available / equipped states
- mobile and landscape layouts

## Language reconstruction

Legacy sci-fi-facing cosmetic names are reinterpreted without changing IDs. Examples:

- `void` → COATED
- `ember` → KRAFT
- `amethyst` → RISOGRAPH
- `aurora` → OFFSET
- `core` → SOLID
- `reactor` → TARGET
- `beam` → GRAPHITE
- `laser` → DOUBLE CUT
- `rift` → OFFSET CUT
- `implode` → PUNCH
- `vacuum` → RING

## Compatibility boundary

VD5 does not change:

- cosmetic IDs
- unlock predicates
- existing save payload structure
- loadout slot structure
- scoring
- progression
- simulation
- replay verification
- generation contracts
- VD1 renderer ownership
- VD2 HUD ownership
- VD3 shell ownership
- VD4 secondary-screen ownership

Existing saves containing the old internal IDs continue to resolve normally.

## Runtime audit

`window.VoidcutCosmetics.audit()` exposes VD5 ownership and verifies the material library, live specimen, semantic category names and legacy ID preservation.
