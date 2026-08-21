# VD3 — Product Shell Reconstruction

VD3 rebuilds VOIDCUT's non-gameplay shell around the VD0–VD2 CUTFORM system.

## Scope

- Main menu composition and artwork
- Shared primary / secondary controls
- Shared overlay and navigation shell
- Pause presentation
- Results presentation
- Screen-cut transition and rank-up shell styling
- Product-level copy cleanup where old neon/void-HUD language was purely decorative

## Preserved

VD3 does not alter:

- deterministic simulation
- collision or cut resolution
- scoring or balance
- chamber / arena / director generation
- replay serialization or verification
- saves or migration
- mastery logic
- cosmetic unlock logic
- VD1 renderer ownership
- VD2 in-run HUD ownership

## Visual contract

The product shell must use:

- semantic `--vc-*` tokens
- flat opaque surfaces
- 0 / 2 / 6 px radius language
- hard contact/object shadows
- editorial grotesk typography
- physical cut/material imagery
- no bloom, glassmorphism, neon gradients, holographic panels, or cyan/magenta split branding

## Main-menu identity

The previous neon vector showcase is replaced by an authored CUTFORM field study built from a physical arena sheet, exposed substrate, offset cut piece, graphic discs, and one scored cut.

## Runtime audit

`window.VoidcutShell.audit()` reports the active VD3 shell contract.

## Intentional boundary

Records, Competition, Mastery, Cosmetics, Settings, Diagnostics, and the replay console retain their existing content architecture in VD3. Shared controls/navigation inherit the new shell primitives, while full screen-specific reconstruction belongs to later phases.
