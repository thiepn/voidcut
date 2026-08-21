from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
text = INDEX.read_text(encoding='utf-8')

if 'name="voidcut-visual-phase" content="VD4"' not in text:
    raise SystemExit('Expected VD4 baseline')
if '/* === VD4 CERTIFICATION CORRECTIONS' in text:
    print('VD4 certification corrections already applied')
    raise SystemExit(0)

old = "board.innerHTML='<div class=\"competition-head\"><span>#</span><span>SCORE</span><span>CHAMBER</span><span>TIME</span></div>'"
new = "board.innerHTML='<div class=\"competition-head\"><span>RANK</span><span>SCORE</span><span>CHAMBER</span><span>TIME</span></div>'"
if text.count(old) != 1:
    raise SystemExit(f'competition header: expected 1 match, found {text.count(old)}')
text = text.replace(old, new, 1)

CSS = r'''
/* === VD4 CERTIFICATION CORRECTIONS ======================================= */
#competitionPanel .competition-row:nth-child(2)::before{display:none!important;content:none!important}
#competitionPanel .competition-row:nth-child(2){box-shadow:inset 5px 0 0 var(--vc-accent)!important}
#competitionPanel .competition-head span:first-child{font-size:9px!important;letter-spacing:.04em!important}
#masteryPanel .mastery-card.complete .mastery-card-points{margin-right:92px!important}
#masteryPanel .mastery-card.complete::after{top:14px!important;right:14px!important}
#recordsPanel .record-value{max-width:100%!important;overflow:hidden!important;text-overflow:ellipsis!important;white-space:nowrap!important}
@media(max-width:480px){
 #masteryPanel .mastery-card.complete .mastery-card-points{margin-right:76px!important}
 #recordsPanel .record-card.featured .record-value{font-size:clamp(24px,7vw,30px)!important}
}
'''
if text.count('</style>') != 1:
    raise SystemExit('Expected one </style>')
text = text.replace('</style>', CSS + '\n</style>', 1)
INDEX.write_text(text, encoding='utf-8')
print('VD4 certification corrections applied')
