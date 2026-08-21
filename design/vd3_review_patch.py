from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
text = INDEX.read_text(encoding='utf-8')
MARK = '/* === VD3 REVIEW CORRECTIONS ============================================== */'

if MARK in text:
    print('VD3 review corrections already applied')
    raise SystemExit(0)
if 'name="voidcut-visual-phase" content="VD3"' not in text:
    raise SystemExit('VD3 shell baseline missing')

css = r'''

/* === VD3 REVIEW CORRECTIONS ============================================== */
#menu.hidden{display:none!important}

/* Shell controls that remain visible over gameplay. */
#pauseBtn{
  width:42px!important;height:42px!important;border-radius:var(--vc-radius-1)!important;background:var(--vc-surface)!important;
  color:var(--vc-ink)!important;border:1px solid var(--vc-line-strong)!important;box-shadow:2px 3px 0 var(--vc-shadow)!important;
  text-shadow:none!important;filter:none!important;font:800 14px var(--vc-font-sans)!important;
}
#pauseBtn:active{transform:translate(2px,3px)!important;box-shadow:none!important}
#tutorial{
  border-radius:var(--vc-radius-1)!important;background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;
  border:1px solid var(--vc-line-strong)!important;border-left:6px solid var(--vc-accent)!important;box-shadow:3px 4px 0 var(--vc-shadow)!important;
  backdrop-filter:none!important;text-shadow:none!important;
}
#tutorial .tutorial-kicker{color:var(--vc-accent)!important;font-family:var(--vc-font-mono)!important}
.mastery-toast,.cosmetic-toast{
  border-radius:var(--vc-radius-1)!important;background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;
  border:1px solid var(--vc-line-strong)!important;box-shadow:4px 5px 0 var(--vc-shadow)!important;backdrop-filter:none!important;
}
.mastery-toast strong,.cosmetic-toast strong{color:var(--vc-ink)!important;text-shadow:none!important}.mastery-toast span,.cosmetic-toast span,.cosmetic-toast em{color:var(--vc-ink-muted)!important}.cosmetic-toast-glyph{color:var(--vc-accent)!important;text-shadow:none!important}

/* Result data is physical even when generated markup uses legacy class names. */
.stats>div{background:var(--vc-surface)!important;color:var(--vc-ink)!important;border:0!important;border-radius:0!important;box-shadow:none!important}
#newBest:not(:empty){display:inline-block!important;margin-top:8px!important;padding:5px 8px!important;background:var(--vc-accent)!important;color:var(--vc-on-accent)!important;border-radius:0!important;font:800 10px var(--vc-font-mono)!important;transform:rotate(-1deg)!important}

/* Hard editorial result motion: no blur, glow or springy HUD choreography. */
#result.motion-sequence .result-identity{animation:vd3ResultIdentity var(--vc-duration-nav) var(--vc-ease-ui) both!important}
#result.motion-sequence .result-score-stage{animation:vd3ResultScore 360ms var(--vc-ease-physical) 60ms both!important}
#result.motion-sequence .result-data{animation:vd3ResultData var(--vc-duration-physical) var(--vc-ease-ui) 150ms both!important}
#result.motion-sequence .result-actions{animation:vd3ResultActions var(--vc-duration-physical) var(--vc-ease-ui) 250ms both!important}
#result.motion-sequence .result-hint{animation:vd3ResultActions var(--vc-duration-nav) var(--vc-ease-ui) 320ms both!important}
@keyframes vd3ResultIdentity{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
@keyframes vd3ResultScore{from{opacity:0;transform:translate(8px,10px)}to{opacity:1;transform:none}}
@keyframes vd3ResultData{from{opacity:0;transform:translateX(10px)}to{opacity:1;transform:none}}
@keyframes vd3ResultActions{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

.rank-up-fx.run .rank-up-card{animation:vd3RankCard 720ms var(--vc-ease-physical) both!important}.rank-up-fx.run .rank-up-glyph{animation:vd3RankGlyph 720ms var(--vc-ease-physical) both!important}
@keyframes vd3RankCard{0%{transform:translate(8px,10px);opacity:0}45%{opacity:1}100%{transform:none;opacity:1}}
@keyframes vd3RankGlyph{0%{transform:rotate(35deg) scale(.72);opacity:0}100%{transform:rotate(225deg) scale(1);opacity:1}}

@media(max-width:700px){#pauseBtn{width:40px!important;height:40px!important}.mastery-toast,.cosmetic-toast{max-width:calc(100vw - 24px)!important}}
'''

style_end = text.index('</style>')
text = text[:style_end] + css + '\n' + text[style_end:]
INDEX.write_text(text, encoding='utf-8')
print('VD3 review corrections applied')
