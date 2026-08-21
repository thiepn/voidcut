# VD2 — Gameplay HUD Reconstruction

VD2 rebuilds the entire in-run information layer on top of the VD1 CUTFORM playfield. The simulation and renderer geometry remain unchanged.

## Reconstructed in VD2

- gameplay wordmark and run-mode identity
- score presentation and score-pulse hierarchy
- combo / multiplier presentation
- field-clear progress as a physical ruler rather than a luminous gradient
- target marker and live cut-safety state
- chamber index and special-field label
- Daily / Duel competitive status moved into the canvas information system
- tutorial header rebuilt as a physical three-column teaching panel
- modifier field language rebuilt as restrained printed patterns
- modifier badge rebuilt as a structural tab
- modifier briefing rebuilt as a physical information card
- milestone field language rebuilt without glow or radial lighting
- milestone badge rebuilt as a structural milestone tab
- milestone briefing rebuilt as an editorial event card
- score / quality / close-call popups rebuilt as flat physical labels

## Explicitly removed from active HUD ownership

- translucent rounded neon HUD container
- cyan/magenta HUD gradients
- glowing score typography
- italic condensed sci-fi wordmark treatment
- luminous progress bar
- neon modifier badges
- animated light-sweep milestone briefing
- DOM Daily/Duel banner ownership

## Preserved exactly

VD2 does not alter simulation, collisions, cut resolution, scoring math, balance, chamber generation, director behavior, save schema, replay schema/verification, progression, mastery, cosmetic unlocks, or the VD1 physical renderer.

## Runtime audit

VD2 exposes `window.VoidcutHUD.audit()` with the HUD version and invariants including `flatPanels: true`, `neonHud: false`, `glowTypography: false`, and `canvasCompetitiveStatus: true`.

## Scope boundary

Menus, pause/results screens, settings, mastery, records, competition, cosmetics, replay console and the broader product shell still contain v6 visual language. Those surfaces belong to later VD phases rather than being mixed into the in-run HUD migration.