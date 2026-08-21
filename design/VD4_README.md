# VD4 — Secondary Screen Reconstruction

## Scope

VD4 reconstructs the information-heavy secondary product screens on top of the VD0–VD3 CUTFORM system:

- Records
- Competition
- Mastery
- shared masthead/header grammar used by those screens
- statistical, leaderboard, challenge and reward presentation

The phase deliberately does **not** redesign Cosmetics, Settings, Diagnostics or the replay console. Those retain their existing feature architecture until later phases.

## Visual model

### Records — archive poster

Records is treated as a statistical archive rather than a dashboard. Headline records become large editorial values; supporting groups are separated by rules and material bands rather than floating rounded cards.

### Competition — race sheet

Competition is treated as a deterministic head-to-head race sheet. The target block becomes a split physical composition, `VS` is structural rather than ornamental, and the leaderboard becomes a restrained ranked table.

### Mastery — challenge book

Mastery is treated as a finite printed challenge book. Rank, reward track, category tabs and challenge cards use hard rules, stamps and progress bars rather than neon panels.

## Preserved contracts

VD4 does not alter:

- simulation
- collision or cut resolution
- scoring math
- balance
- arena/chamber/director generation
- saves
- replay serialization or verification
- competition ranking logic
- mastery challenge definitions, progression or rewards
- cosmetic state
- VD1 renderer ownership
- VD2 gameplay HUD ownership
- VD3 shell ownership

## Runtime audit

`window.VoidcutSecondaryScreens.audit()` exposes VD4 ownership and reports invariants for the three reconstructed screens.

## Acceptance gates

- visual phase metadata reports `VD4`
- Records, Competition and Mastery use VD4 mastheads
- legacy circular/glowing screen marks are absent from those three active screen headers
- ranked competition rows use zero-padded editorial ranks
- CUTFORM semantic tokens own the new screen surfaces and typography
- VD1, VD2 and VD3 runtime contracts remain present
- release metadata remains build 6.0.0 / save 16 / replay 8 / arena 2 / director 6 / daily 1
- document parses as HTML
- complete monolithic inline JavaScript passes `node --check`
