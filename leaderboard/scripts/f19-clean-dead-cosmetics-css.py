from pathlib import Path

root = Path(__file__).resolve().parents[2]
index_path = root / 'index.html'
register_path = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

html = index_path.read_text(encoding='utf-8')

# Remove only branches that are unreachable because these IDs are already
# returned by the unconditional/default cosmetic set at the top of the helper.
for old, label in [
    ("if(id==='aurora')return s.deepestChamber>=12;", 'dead aurora unlock branch'),
    ("if(id==='reactor')return(s.totalRuns||0)>=10;", 'dead reactor unlock branch'),
    ("if(id==='ribbon')return r.fastestClear!=null&&r.fastestClear<=20;", 'dead ribbon unlock branch'),
    ("if(id==='laser')return(r.largestCut||0)>=40;", 'dead laser unlock branch'),
    ("if(id==='vacuum')return s.deepestChamber>=15;", 'dead vacuum unlock branch'),
]:
    html = replace_once(html, old, '', label)

signature_cut = '''/* Signature cut transition. It is intentionally short: identity, not obstruction. */
.vc-screen-cut{position:fixed;inset:0;z-index:9998;pointer-events:none;overflow:hidden;opacity:0;--cut-a:#2de2ff;--cut-b:#ff2d9e}
.vc-screen-cut[data-tone="cyan"]{--cut-a:#2de2ff;--cut-b:#9bf6ff}
.vc-screen-cut[data-tone="magenta"]{--cut-a:#ff2d9e;--cut-b:#ff88c7}
.vc-screen-cut .cut-pane,.vc-screen-cut .cut-beam{position:absolute;left:-32vw;top:50%;width:164vw;transform-origin:center}
.vc-screen-cut .cut-pane{height:52vh;background:linear-gradient(180deg,rgba(1,4,9,0),rgba(1,4,9,.78));filter:drop-shadow(0 0 16px rgba(0,0,0,.45))}
.vc-screen-cut .cut-pane-a{transform:translateY(-100%) rotate(-18deg)}
.vc-screen-cut .cut-pane-b{transform:translateY(0) rotate(-18deg);background:linear-gradient(0deg,rgba(1,4,9,0),rgba(1,4,9,.70))}
.vc-screen-cut .cut-beam{height:2px;background:linear-gradient(90deg,transparent 4%,var(--cut-a) 32%,#fff 50%,var(--cut-b) 68%,transparent 96%);box-shadow:0 0 6px var(--cut-a),0 0 18px color-mix(in srgb,var(--cut-a) 55%,transparent);transform:rotate(-18deg) translateY(-1px)}
.vc-screen-cut.run{opacity:1;animation:vcCutShell var(--motion-ui) linear both}
.vc-screen-cut.run .cut-pane-a{animation:vcCutPaneA var(--motion-ui) var(--motion-ease) both}
.vc-screen-cut.run .cut-pane-b{animation:vcCutPaneB var(--motion-ui) var(--motion-ease) both}
.vc-screen-cut.run .cut-beam{animation:vcCutBeam var(--motion-ui) var(--motion-ease) both}
@keyframes vcCutShell{0%,100%{opacity:0}12%,78%{opacity:1}}
@keyframes vcCutBeam{0%{transform:translateX(-38vw) rotate(-18deg);opacity:0}18%{opacity:1}72%{opacity:1}100%{transform:translateX(38vw) rotate(-18deg);opacity:0}}
@keyframes vcCutPaneA{0%{transform:translateX(-34vw) translateY(-100%) rotate(-18deg);opacity:0}28%{opacity:.72}100%{transform:translateX(36vw) translateY(-106%) rotate(-18deg);opacity:0}}
@keyframes vcCutPaneB{0%{transform:translateX(-34vw) translateY(0) rotate(-18deg);opacity:0}28%{opacity:.62}100%{transform:translateX(36vw) translateY(6%) rotate(-18deg);opacity:0}}
'''
html = replace_once(html, signature_cut, '', 'dead signature-cut CSS block')

reduced_motion = '''body:has(.toggle[data-setting="reducedMotion"].is-on) .vc-screen-cut,
body:has(.toggle[data-setting="reducedMotion"].is-on) .rank-up-fx{display:none!important}'''
html = replace_once(
    html,
    reduced_motion,
    'body:has(.toggle[data-setting="reducedMotion"].is-on) .rank-up-fx{display:none!important}',
    'dead screen-cut reduced-motion selector',
)

physical_cut = '''/* Screen-cut transition becomes two physical sheets separating. */
.vc-screen-cut{--cut-a:var(--vc-accent)!important;--cut-b:var(--vc-accent-alt)!important;background:transparent!important}
.vc-screen-cut .cut-pane{height:56vh!important;background:var(--vc-surface)!important;filter:none!important;border:2px solid var(--vc-line-strong)!important;box-shadow:0 8px 0 var(--vc-shadow)!important}
.vc-screen-cut .cut-beam{height:7px!important;background:var(--vc-substrate)!important;box-shadow:none!important;border-top:2px solid var(--vc-accent)!important}

'''
html = replace_once(html, physical_cut, '', 'dead physical screen-cut CSS block')

if '.vc-screen-cut' in html:
    raise SystemExit('unexpected .vc-screen-cut reference remains after cleanup')
for token in ['vcCutShell', 'vcCutBeam', 'vcCutPaneA', 'vcCutPaneB']:
    if token in html:
        raise SystemExit(f'unexpected dead keyframe remains: {token}')

index_path.write_text(html, encoding='utf-8')

reg = register_path.read_text(encoding='utf-8')
row22 = '| VC-022 | LOW | Cosmetic unlock logic contains unreachable/conflicting branches for IDs already returned as always unlocked. | F19 | OPEN |'
row23 = '| VC-023 | LOW | Obsolete `.vc-screen-cut` hide rule remains even though the popup DOM/function/calls were removed. | F19 | OPEN |'
reg = replace_once(reg, row22, row22.replace('OPEN', 'FIXED — VERIFYING'), 'VC-022 register row')
reg = replace_once(reg, row23, row23.replace('OPEN', 'FIXED — VERIFYING'), 'VC-023 register row')
reg += '''\n## F19 implementation record — dead cosmetic branches and screen-cut CSS cleanup\n\n- `cosmeticUnlocked()` keeps its existing unconditional IDs exactly as-is. The unreachable later conditions for `aurora`, `reactor`, `ribbon`, `laser`, and `vacuum` were removed because those IDs already return `true` before any threshold branch can execute. No cosmetic unlock outcome changes.\n- All live conditional unlock branches remain intact (`ember`, `amethyst`, `monochrome`, `hollow`, `prism`, `eclipse`, `comet`, `echo`, `sparks`, `blade`, `arc`, `rift`, `shatter`, `dissolve`, `fracture`).\n- The complete dead `.vc-screen-cut` CSS family was removed, including tone/pane/beam/run rules, `vcCutShell`/`vcCutBeam`/`vcCutPaneA`/`vcCutPaneB` keyframes, the reduced-motion screen-cut selector, and the later physical-sheet overrides.\n- The unrelated reduced-motion `.rank-up-fx` hide rule remains.\n- No screen-cut DOM/runtime path is reintroduced. No save schema, gameplay, scoring, replay, leaderboard, PWA, tutorial, cosmetic IDs/descriptions/defaults, or actual unlock requirements changed.\n'''
register_path.write_text(reg, encoding='utf-8')
