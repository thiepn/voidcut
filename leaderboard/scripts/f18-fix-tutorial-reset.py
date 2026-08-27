from pathlib import Path

root = Path(__file__).resolve().parents[2]
index_path = root / 'index.html'
register_path = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'

html = index_path.read_text(encoding='utf-8')
start = html.index('function configureTutorialStage(stage,step=null){')
end = html.index('\nfunction refreshTutorialPrompt()', start)
old = html[start:end]
required_old = [
    'const a=tutorialArena();sim.seed=(0x47C000+stage)>>>0;',
    'sim.runElapsed=0;',
    'sim.score=0;',
    'sim.nextR=2;sim.nextB=10;',
    'sim.plan={directorGen:4,',
]
for token in required_old:
    if token not in old:
        raise SystemExit(f'configureTutorialStage drift: missing {token}')

new = "function configureTutorialStage(stage,step=null){clearTimeout(tutorialTimer);tutorialLocked=false;tutorialStage=stage;tutorialStep=step||(stage===1?'collapse':stage===2?'setupDivider':'scoring');const seed=(0x47C000+stage)>>>0;sim.reset(seed,2,4,9);sim.seed=seed;sim.rng=new RNG(seed);sim.previousArena=null;sim.previousStyle=null;sim.previousTempo=null;sim.previousPressure=null;sim.previousModifier=null;sim.briefingRemaining=0;sim.modifierTick=-1;sim.chamber=stage;sim.nextR=2;sim.nextB=10;const a=tutorialArena();sim.arena=a;sim.regions=[{id:1,v:a.v.map(q=>({...q}))}];sim.area=a.area;sim.removed=0;sim.cut=null;sim.chamberCuts=0;sim.chamberElapsed=0;sim.chamberRemovalCuts=0;sim.chamberDividerCuts=0;sim.chamberRemovedPct=0;sim.chamberCloseCalls=0;sim.plan={directorGen:4,arenaType:'rectangle',style:'training',tempo:'breather',flow:'TRAINING',arc:`LESSON ${stage}`,balls:stage===1?1:2,types:stage===1?['standard']:['standard','standard'],mult:.35,speed:0,cut:520,pressure:1,target:1,arenaRisk:1,reaction:.35};if(stage===1)sim.balls=[tutorialCore(1,AX+AW*.28,AY+AH*.52)];else sim.balls=[tutorialCore(1,AX+AW*.28,AY+AH*.48),tutorialCore(2,AX+AW*.72,AY+AH*.52)];rebuildRenderGeometry();shownScore=0;hudMultiplier=1;hudCombo=0;bounceState.clear();clearFx();acc=0;last=performance.now();refreshTutorialPrompt()}"
html = html[:start] + new + html[end:]
index_path.write_text(html, encoding='utf-8')

reg = register_path.read_text(encoding='utf-8')
old_row = '| VC-021 | MEDIUM | Tutorial initialization partially mutates the current simulation instead of fully resetting generation/scoring/briefing state. | F18 | OPEN |'
new_row = '| VC-021 | MEDIUM | Tutorial initialization partially mutates the current simulation instead of fully resetting generation/scoring/briefing state. | F18 | FIXED — VERIFYING |'
if reg.count(old_row) != 1:
    raise SystemExit(f'VC-021 register row: expected 1 match, found {reg.count(old_row)}')
reg = reg.replace(old_row, new_row, 1)
reg += '''\n## F18 implementation record — canonical simulation reset before tutorial geometry\n\n- Every entry into `configureTutorialStage()` now begins from the canonical simulation reset path: `sim.reset(seed, 2, 4, 9)`. Tutorial initialization no longer depends on a hand-maintained subset of run/scoring fields.\n- The tutorial uses arena generation 2, director generation 4 and scoring version 9. Director generation 4 matches the tutorial training plan and prevents generation-5/6 briefing gates from leaking into training input.\n- After the canonical reset's throwaway generated chamber, tutorial setup resets the RNG to the deterministic lesson seed and explicitly clears generated-history fields (`previousArena`, `previousStyle`, `previousTempo`, `previousPressure`, `previousModifier`), `briefingRemaining`, and `modifierTick` before installing training geometry.\n- Canonical reset therefore owns run clock, score/stat accumulators, generation/scoring contracts, current chamber transient state and baseline entity state; the tutorial code only applies lesson-specific chamber number, deterministic arena/cores, plan and rendering/HUD state.\n- Lesson retries and lesson transitions also pass through the same full reset because both call `configureTutorialStage()`.\n- No gameplay balance, normal-run generation, replay format, leaderboard behavior, save schema, PWA behavior or visual design changed in F18.\n'''
register_path.write_text(reg, encoding='utf-8')
