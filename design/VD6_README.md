# VOIDCUT VD6 — System & Utility Reconstruction

VD6 reconstructs the remaining technical/player-utility surfaces as a quiet CUTFORM instrument/manual layer.

## Scope

- Settings
- Diagnostics / System Checks
- Replay Console
- Save export/import and report actions
- Utility warnings and short-lived technical states
- Theme/texture controls

## Visual model

Technical screens are intentionally less theatrical than gameplay. They use ledger rows, hard rules, release-contract strips, report sheets, compact monospace readouts, physical controls and restrained semantic accents.

### Settings

Settings becomes a numbered system manual rather than a rounded dashboard. Existing setting keys and controls remain unchanged. The visual palette control is relabeled **Theme**, and a separate **Texture** preference exposes the VD0 full/reduced/off texture modes without changing the save schema.

### Theme bridge

The persisted `settings.colorTheme` values remain stable for save compatibility and existing Mastery unlock logic:

| Persisted ID | CUTFORM theme |
| --- | --- |
| `arcade` | Paper |
| `sunset` | Carbon |
| `ion` | Cobalt |
| `ice` | Kelp |
| `vector` | Plum |
| `spectrum` | Mono |

No save migration is required. Existing Vector/Spectrum unlock thresholds continue to gate the mapped Plum/Mono themes.

### Diagnostics

Diagnostics becomes a release instrument with a visible contract strip, one readable report surface, grouped verification/data actions and a data-safety note. Diagnostic behavior is unchanged.

### Replay

Replay becomes a compact inspection ruler over the gameplay field. All existing highlight, seek, pause, speed, previous/next cut and exit controls remain intact.

## Compatibility boundary

VD6 must not change:

- simulation
- scoring or balance
- save schema or setting keys
- replay format or verification
- diagnostic test definitions
- data import/export formats
- arena/director/daily generation
- progression or cosmetic unlock logic

Release contracts remain build 6.0.0, save 16, replay 8, arena 2, director 6, daily 1.

## Runtime audit

`window.VoidcutUtilities.audit()` reports VD6 ownership, the Settings manual, theme bridge, texture control, release instrument, replay instrument, legacy-neon-copy status and release contracts.
