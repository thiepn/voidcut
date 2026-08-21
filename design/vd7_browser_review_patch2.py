from pathlib import Path

p=Path('index.html')
t=p.read_text(encoding='utf-8')
marker='/* === VD7 BROWSER REVIEW CORRECTIONS II ================================= */'
if marker in t:
    print('VD7 browser review corrections II already present')
    raise SystemExit(0)

block=r'''

/* === VD7 BROWSER REVIEW CORRECTIONS II ================================= */
/* Second rendered pass: neutralize only the residual pseudo-element chrome
   and fixed-height rules reported by Chromium. */
#menu .primary-icon::after{filter:none!important;box-shadow:none!important}
.screen-hero::after{
  background:linear-gradient(90deg,var(--vc-accent),color-mix(in srgb,var(--vc-line) 70%,transparent) 38%,color-mix(in srgb,var(--vc-line) 70%,transparent) 72%,var(--vc-accent-alt))!important;
  box-shadow:none!important;filter:none!important;
}
.screen-nav .screen-back,.cos-back{height:46px!important;min-height:46px!important;max-height:none!important}
#recordsPanel .record-card::after,#recordsPanel .record-card.featured::after{background:color-mix(in srgb,var(--vc-accent) 18%,transparent)!important;box-shadow:none!important;filter:none!important}
#recordsPanel .record-card.featured:nth-child(even)::after{background:color-mix(in srgb,var(--vc-accent-alt) 16%,transparent)!important}
#masteryPanel .mastery-rank-emblem::after{background:transparent!important;border-color:var(--vc-accent-alt)!important;box-shadow:none!important;filter:none!important}
#cosHeroArt.cos-hero-art::after{display:none!important;content:none!important;background:none!important;box-shadow:none!important;filter:none!important}
#replayBadge::before{background:var(--vc-accent)!important;box-shadow:none!important;filter:none!important}
'''

if '\n</style>' not in t:
    raise SystemExit('style close marker missing')
t=t.replace('\n</style>',block+'\n</style>',1)
p.write_text(t,encoding='utf-8')
print('VD7 browser review corrections II applied')
print('HTML bytes:',len(t.encode('utf-8')))
