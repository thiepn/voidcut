from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
text = INDEX.read_text(encoding='utf-8')

if 'name="voidcut-visual-phase" content="VD3"' in text:
    print('VD3 shell already applied')
    raise SystemExit(0)

if 'name="voidcut-visual-phase" content="VD2"' not in text:
    raise SystemExit('Expected VD2 baseline')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    if text.count(old) != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {text.count(old)}')
    text = text.replace(old, new, 1)


replace_once(
    '<meta name="theme-color" content="#050b11" />',
    '<meta name="theme-color" content="#E9E4D8" />',
    'theme color',
)
replace_once(
    '<meta name="description" content="VOIDCUT — a precision neon-vector arcade game about cutting away empty space, protecting cores, mastering chambers, and racing deterministic runs." />',
    '<meta name="description" content="VOIDCUT — a precision arcade game about cutting away space, protecting moving nodes, mastering stages, and racing deterministic runs." />',
    'description',
)
replace_once(
    '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />',
    '<meta name="apple-mobile-web-app-status-bar-style" content="default" />',
    'apple status bar',
)
replace_once('<title>VOIDCUT — Visual Release</title>', '<title>VOIDCUT</title>', 'title')
replace_once(
    '<meta name="voidcut-visual-phase" content="VD2">',
    '<meta name="voidcut-visual-phase" content="VD3">',
    'visual phase',
)
replace_once('PRECISION <span>•</span> RISK <span>•</span> VOID', 'CUT <span>/</span> CLEAR <span>/</span> SURVIVE', 'menu tagline')
replace_once('CUT CLEAN. PUSH DEEPER. SURVIVE THE VOID.', 'CUT SPACE. KEEP CONTROL. GO FURTHER.', 'menu hint')
replace_once('RUN // SUSPENDED', 'RUN / PAUSED', 'pause kicker')
replace_once('THE VOID WAITS', 'RUN HELD', 'pause footer')
replace_once('RUN // COMPLETE', 'RUN / COMPLETE', 'result eyebrow')
replace_once('VOID MASTERY // RANK ADVANCE', 'MASTERY / RANK ADVANCE', 'rank copy')

menu_start = text.index('    <div class="menu-stage" aria-hidden="true">')
menu_end = text.index('    <div id="best" class="best">', menu_start)
menu_markup = r'''    <div class="menu-stage" aria-hidden="true">
      <svg class="vd3-menu-art" viewBox="0 0 760 700" preserveAspectRatio="xMidYMid slice">
        <rect class="vd3-art-ground" width="760" height="700"/>
        <g class="vd3-register">
          <path d="M56 58h34M73 41v34M670 58h34M687 41v34M56 642h34M73 625v34M670 642h34M687 625v34"/>
        </g>
        <path class="vd3-material-shadow" d="M126 134 598 92 676 208 630 548 514 618 150 570 86 432Z"/>
        <path class="vd3-material" d="M118 124 590 82 668 198 622 538 506 608 142 560 78 422Z"/>
        <path class="vd3-offcut-shadow" d="M420 326 657 193 621 410 528 474Z"/>
        <path class="vd3-offcut" d="M411 315 648 182 612 399 519 463Z"/>
        <path class="vd3-cut-trench" d="M146 493 635 218"/>
        <path class="vd3-cut-score" d="M146 493 635 218"/>
        <g class="vd3-node vd3-node-a"><circle cx="270" cy="250" r="34"/><path d="M252 250h36M270 232v36"/></g>
        <g class="vd3-node vd3-node-b"><circle cx="458" cy="486" r="29"/><path d="m446 476 24 20M470 476l-24 20"/></g>
        <g class="vd3-node vd3-node-c"><circle cx="532" cy="214" r="22"/><circle cx="532" cy="214" r="7"/></g>
        <g class="vd3-edge-marks"><path d="M117 124h38M118 124v35M621 538h-40M622 538v-35M142 560h40M142 560v-35"/></g>
        <g class="vd3-measure"><path d="M104 610h238"/><path d="M104 602v16M144 605v10M184 605v10M224 605v10M264 605v10M304 605v10M342 602v16"/></g>
      </svg>
      <div class="hero-art-label"><span>FIELD STUDY / 01</span><strong>MAKE SPACE.</strong><em>Cut the material. Keep the nodes.</em></div>
      <div class="stage-score hidden"><span>SCORE</span><strong id="menuStageScore">0</strong></div>
      <div class="stage-mult hidden"><strong>×3.2</strong><span>MULTIPLIER</span></div>
      <div class="stage-grid hidden"></div><div class="stage-poly stage-poly-a hidden"></div><div class="stage-poly stage-poly-b hidden"></div><div class="stage-poly stage-poly-c hidden"></div><div class="stage-shard stage-shard-a hidden"></div><div class="stage-shard stage-shard-b hidden"></div><div class="stage-split split-left hidden"></div><div class="stage-split split-right hidden"></div><div class="stage-orb hidden"></div><div class="stage-objectives hidden"></div><div class="stage-directive hidden"></div>
    </div>
'''
text = text[:menu_start] + menu_markup + text[menu_end:]

css = r'''

/* === VD3 CUTFORM PRODUCT SHELL ============================================
   Owns the main menu, shared shell controls, pause, results and shell motion.
   Secondary feature-screen content remains intentionally outside VD3. */
:root{
  --vd3-max:1320px;
  --vd3-hard-shadow:6px 7px 0 var(--vc-shadow);
  --vd3-hard-shadow-small:3px 4px 0 var(--vc-shadow);
}
html,body{font-family:var(--vc-font-sans)!important;background:var(--vc-bg)!important;color:var(--vc-bg-ink)!important}
body{background-image:none!important}
#wrap::before,#wrap::after{display:none!important}
button:focus-visible,input:focus-visible,summary:focus-visible{outline:2px solid var(--vc-focus)!important;outline-offset:3px!important}

/* Shared shell: opaque page, static material grain, no glass layers. */
.overlay{
  background:var(--vc-bg)!important;
  color:var(--vc-bg-ink)!important;
  font-family:var(--vc-font-sans)!important;
  padding:max(24px,env(safe-area-inset-top)) max(24px,env(safe-area-inset-right)) max(24px,env(safe-area-inset-bottom)) max(24px,env(safe-area-inset-left))!important;
}
.overlay::before{
  content:""!important;display:block!important;position:fixed!important;inset:0!important;pointer-events:none!important;z-index:-1!important;
  background-image:var(--vc-grain-image)!important;background-size:96px 96px!important;opacity:calc(var(--vc-grain-opacity)*.48)!important;
  mix-blend-mode:multiply!important;mask-image:none!important;
}
.overlay::after{display:none!important}
.pause-title,.result-title,.logo-lockup{font-family:var(--vc-font-sans)!important}
.screen-subtitle{color:var(--vc-bg-ink-muted)!important}

/* Shared physical controls. */
.primary,.secondary,.daily-run-card,.menu-tile,.menu-orb-button,.toggle,.cos-back,.mastery-tab,.cos-cat-tab,.replay-controls button,.replay-highlights button,.replay-exit,.cos-loadout-actions button{
  border-radius:var(--vc-radius-1)!important;
  font-family:var(--vc-font-sans)!important;
  transition:transform var(--vc-duration-press) var(--vc-ease-ui),box-shadow var(--vc-duration-press) var(--vc-ease-ui),background-color var(--vc-duration-nav) var(--vc-ease-ui),border-color var(--vc-duration-nav) var(--vc-ease-ui)!important;
  backdrop-filter:none!important;filter:none!important;
}
.primary{
  background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;border:2px solid var(--vc-line-strong)!important;
  border-left:8px solid var(--vc-accent)!important;box-shadow:var(--vd3-hard-shadow)!important;text-shadow:none!important;
  letter-spacing:.01em!important;font-weight:800!important;
}
.primary::after{display:none!important}
.secondary{
  background:var(--vc-surface)!important;color:var(--vc-ink)!important;border:1px solid var(--vc-line)!important;
  box-shadow:var(--vd3-hard-shadow-small)!important;text-shadow:none!important;
}
.primary:hover,.secondary:hover,.menu-tile:hover,.daily-run-card:hover,.menu-orb-button:hover{transform:translate(-1px,-1px)!important;border-color:var(--vc-line-strong)!important;filter:none!important}
.primary:active,.secondary:active,.menu-tile:active,.daily-run-card:active,.menu-orb-button:active{transform:translate(3px,4px)!important;box-shadow:none!important}
[data-vc-icon]::before{filter:none!important}

/* Persistent navigation becomes a printed page header. */
.screen-nav{
  position:sticky!important;top:0!important;min-height:52px!important;margin:-8px 0 14px!important;padding:8px 0!important;
  background:var(--vc-bg)!important;border-bottom:1px solid var(--vc-line)!important;backdrop-filter:none!important;
}
.screen-nav .screen-nav-brand{font:700 11px var(--vc-font-mono)!important;color:var(--vc-bg-ink-muted)!important;letter-spacing:.08em!important}
.screen-nav .screen-back{
  min-width:104px!important;min-height:40px!important;border-radius:var(--vc-radius-1)!important;background:var(--vc-surface)!important;
  border:1px solid var(--vc-line)!important;box-shadow:2px 3px 0 var(--vc-shadow)!important;color:var(--vc-ink)!important;
}
.screen-nav .screen-back:hover{background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important}

/* Main menu: editorial composition rather than dashboard. */
#menu{
  display:grid!important;grid-template-columns:minmax(340px,500px) minmax(430px,700px)!important;
  grid-template-rows:auto auto auto auto auto 1fr!important;gap:16px 48px!important;align-content:center!important;justify-content:center!important;
  padding:clamp(28px,4.5vw,68px)!important;background:var(--vc-bg)!important;
}
#menu>.menu-topbar{grid-column:1/-1!important;width:100%!important;max-width:var(--vd3-max)!important;border-bottom:1px solid var(--vc-line)!important;padding-bottom:12px!important}
.menu-orb-button{
  width:46px!important;height:42px!important;min-height:42px!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;
  border:1px solid var(--vc-line)!important;box-shadow:2px 3px 0 var(--vc-shadow)!important;
}
.menu-orb-button span::before{filter:none!important;color:var(--vc-ink)!important}
.menu-status-pill{
  height:42px!important;padding:0 14px!important;border-radius:var(--vc-radius-1)!important;background:var(--vc-surface)!important;
  border:1px solid var(--vc-line)!important;box-shadow:none!important;color:var(--vc-ink)!important;
}
.menu-status-gem{width:8px!important;height:8px!important;border-radius:0!important;transform:none!important;background:var(--vc-accent)!important;box-shadow:none!important}
.menu-status-caption{color:var(--vc-ink-muted)!important;letter-spacing:.08em!important}#menuStatusValue{font-family:var(--vc-font-sans)!important;color:var(--vc-ink)!important}
.logo-lockup{
  grid-column:1!important;grid-row:2!important;position:relative!important;align-self:end!important;font-size:clamp(70px,7vw,110px)!important;
  font-weight:900!important;font-style:normal!important;line-height:.78!important;letter-spacing:-.075em!important;text-shadow:none!important;
}
.logo-lockup::after{content:"";position:absolute;left:47%;top:-4%;width:8px;height:110%;background:var(--vc-bg);border-left:2px solid var(--vc-accent);transform:rotate(19deg);transform-origin:center;pointer-events:none}
.logo-cyan{color:var(--vc-bg-ink)!important}.logo-magenta{color:var(--vc-accent)!important;margin-left:.012em!important}
.menu-tagline{grid-column:1!important;grid-row:3!important;margin:1px 0 0!important;color:var(--vc-bg-ink)!important;font:700 12px var(--vc-font-mono)!important;letter-spacing:.09em!important}
.menu-tagline span{color:var(--vc-accent)!important;opacity:1!important}.version{grid-column:1!important;grid-row:3!important;color:var(--vc-bg-ink-muted)!important;font:600 10px var(--vc-font-mono)!important;letter-spacing:.03em!important}

/* New authored field-study hero. */
.menu-stage{
  grid-column:2!important;grid-row:2/6!important;position:relative!important;min-height:520px!important;max-height:700px!important;overflow:hidden!important;
  border-radius:var(--vc-radius-0)!important;background:var(--vc-substrate)!important;border:2px solid var(--vc-line-strong)!important;
  box-shadow:9px 10px 0 var(--vc-shadow)!important;
}
.menu-stage::before,.menu-stage::after{display:none!important}
.vd3-menu-art{position:absolute;inset:0;width:100%;height:100%;display:block}
.vd3-art-ground{fill:var(--vc-substrate)}
.vd3-register{fill:none;stroke:var(--vc-on-substrate);stroke-width:1.5;opacity:.24}
.vd3-material-shadow,.vd3-offcut-shadow{fill:var(--vc-shadow);opacity:.32;transform:translate(8px,10px)}
.vd3-material,.vd3-offcut{fill:var(--vc-arena);stroke:var(--vc-arena-edge);stroke-width:3;stroke-linejoin:miter}
.vd3-offcut{transform:translate(16px,10px) rotate(1.6deg);transform-origin:530px 330px}
.vd3-offcut-shadow{transform:translate(25px,21px) rotate(1.6deg);transform-origin:530px 330px;opacity:.24}
.vd3-cut-trench{fill:none;stroke:var(--vc-substrate);stroke-width:15;stroke-linecap:butt}
.vd3-cut-score{fill:none;stroke:var(--vc-accent);stroke-width:2.5;stroke-linecap:butt}
.vd3-node circle{stroke:var(--vc-arena-edge);stroke-width:3}.vd3-node path{fill:none;stroke:var(--vc-on-accent);stroke-width:4;stroke-linecap:square}
.vd3-node-a circle{fill:var(--vc-node-a)}.vd3-node-b circle{fill:var(--vc-node-b)}.vd3-node-c circle:first-child{fill:var(--vc-node-c)}.vd3-node-c circle:last-child{fill:var(--vc-on-accent);stroke:none}
.vd3-edge-marks,.vd3-measure{fill:none;stroke:var(--vc-on-substrate);stroke-width:1.5;opacity:.34}
.hero-art-label{
  position:absolute!important;left:24px!important;right:24px!important;bottom:22px!important;display:grid!important;grid-template-columns:auto 1fr!important;
  grid-template-rows:auto auto!important;align-items:end!important;gap:3px 14px!important;padding:16px 18px!important;background:var(--vc-surface)!important;
  border:1px solid var(--vc-line-strong)!important;box-shadow:4px 5px 0 var(--vc-shadow)!important;color:var(--vc-ink)!important;
}
.hero-art-label span{grid-column:1!important;grid-row:1!important;color:var(--vc-ink-muted)!important;font:700 9px var(--vc-font-mono)!important;letter-spacing:.08em!important}
.hero-art-label strong{grid-column:1!important;grid-row:2!important;color:var(--vc-ink)!important;font:900 26px var(--vc-font-sans)!important;letter-spacing:-.035em!important}
.hero-art-label em{grid-column:2!important;grid-row:2!important;justify-self:end!important;align-self:center!important;color:var(--vc-ink-secondary)!important;font:600 11px var(--vc-font-sans)!important;font-style:normal!important}

#best{grid-column:1!important;grid-row:4!important;gap:12px!important;max-width:460px!important;padding:10px 0!important;color:var(--vc-bg-ink)!important}
.best-badge{width:34px!important;height:34px!important;border-radius:var(--vc-radius-0)!important;background:var(--vc-accent)!important;border:2px solid var(--vc-line-strong)!important;box-shadow:2px 3px 0 var(--vc-shadow)!important}
.best-badge-core{width:10px!important;height:10px!important;border-radius:50%!important;transform:none!important;background:var(--vc-on-accent)!important;box-shadow:none!important}
.best-label{color:var(--vc-bg-ink-muted)!important;font-size:10px!important;letter-spacing:.08em!important}.best-value{font-family:var(--vc-font-sans)!important;color:var(--vc-bg-ink)!important}.best-subline{color:var(--vc-accent)!important;letter-spacing:.03em!important}
#play{
  grid-column:1!important;grid-row:5!important;width:min(100%,500px)!important;height:82px!important;padding:12px 22px!important;
  background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;border:2px solid var(--vc-line-strong)!important;border-left:10px solid var(--vc-accent)!important;
  box-shadow:7px 8px 0 var(--vc-shadow)!important;
}
#play .primary-icon{filter:none!important}.primary-text{font-family:var(--vc-font-sans)!important;font-style:normal!important;letter-spacing:-.02em!important}.primary-sub{color:var(--vc-ink-muted)!important;letter-spacing:.04em!important}
.daily-run-card{
  grid-column:1!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;border:1px solid var(--vc-line-strong)!important;
  border-left:6px solid var(--vc-accent-alt)!important;box-shadow:3px 4px 0 var(--vc-shadow)!important;
}
.daily-kicker,.daily-best-label,.daily-rule,.daily-attempts{color:var(--vc-ink-muted)!important}.daily-date,.daily-best{color:var(--vc-ink)!important}
.menu-grid{grid-column:1!important;display:grid!important;grid-template-columns:1fr 1fr!important;gap:0!important;border-top:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important}
.menu-tile{
  min-height:72px!important;border-radius:0!important;background:transparent!important;color:var(--vc-bg-ink)!important;border:0!important;border-bottom:1px solid var(--vc-line)!important;
  box-shadow:none!important;text-align:left!important;padding:12px 10px!important;
}
.menu-tile:nth-child(odd){border-right:1px solid var(--vc-line)!important}.menu-tile:nth-last-child(-n+2){border-bottom:0!important}
.menu-tile:hover{background:color-mix(in srgb,var(--vc-surface) 58%,transparent)!important;transform:none!important}
.tile-icon{border-radius:0!important;background:var(--vc-accent)!important;color:var(--vc-on-accent)!important;box-shadow:none!important}.vc-icon{stroke:currentColor!important;filter:none!important}
.tile-label{color:var(--vc-bg-ink)!important;font-family:var(--vc-font-sans)!important;letter-spacing:.02em!important}.tile-sub{color:var(--vc-bg-ink-muted)!important}
.health-note,.hint{color:var(--vc-bg-ink-muted)!important;font-family:var(--vc-font-mono)!important;letter-spacing:.04em!important}.hint{border-top:1px solid var(--vc-line)!important;padding-top:10px!important}

/* Screen-cut transition becomes two physical sheets separating. */
.vc-screen-cut{--cut-a:var(--vc-accent)!important;--cut-b:var(--vc-accent-alt)!important;background:transparent!important}
.vc-screen-cut .cut-pane{height:56vh!important;background:var(--vc-surface)!important;filter:none!important;border:2px solid var(--vc-line-strong)!important;box-shadow:0 8px 0 var(--vc-shadow)!important}
.vc-screen-cut .cut-beam{height:7px!important;background:var(--vc-substrate)!important;box-shadow:none!important;border-top:2px solid var(--vc-accent)!important}

/* Pause: frozen run remains visible behind one physical sheet. */
#pausePanel{
  display:grid!important;place-items:center!important;background:color-mix(in srgb,var(--vc-substrate) 62%,transparent)!important;
  overflow:hidden!important;backdrop-filter:none!important;
}
#pausePanel.hidden{display:none!important}
.pause-shell{
  width:min(440px,calc(100vw - 40px))!important;margin:0!important;padding:34px!important;background:var(--vc-surface-raised)!important;
  border:2px solid var(--vc-line-strong)!important;border-radius:var(--vc-radius-0)!important;box-shadow:10px 12px 0 var(--vc-shadow)!important;color:var(--vc-ink)!important;
}
.pause-emblem{display:none!important}.pause-kicker{color:var(--vc-ink-muted)!important;font:700 10px var(--vc-font-mono)!important;letter-spacing:.09em!important}.pause-title{margin-top:4px!important;color:var(--vc-ink)!important;font-size:clamp(48px,8vw,72px)!important;letter-spacing:-.055em!important;text-transform:uppercase!important}.pause-divider{height:4px!important;background:var(--vc-accent)!important;border:0!important;margin:20px 0 24px!important}.pause-shell .primary,.pause-shell .secondary{width:100%!important;min-height:52px!important}.pause-actions-secondary{display:grid!important;grid-template-columns:1fr 1fr!important;gap:10px!important;margin-top:14px!important}.pause-exit{margin-top:10px!important}.pause-footer{margin-top:22px!important;padding-top:10px!important;border-top:1px solid var(--vc-line)!important;color:var(--vc-ink-muted)!important;font:700 9px var(--vc-font-mono)!important;letter-spacing:.08em!important}

/* Results: a run-generated editorial poster. */
#result{display:grid!important;place-items:center!important;background:var(--vc-bg)!important;color:var(--vc-bg-ink)!important;overflow:auto!important}
#result.hidden{display:none!important}
.result-atmosphere{position:fixed!important;inset:0!important;overflow:hidden!important;pointer-events:none!important;opacity:1!important}
.result-atmosphere::before{content:"";position:absolute;right:-8vw;top:10vh;width:min(52vw,720px);height:min(52vw,720px);border:clamp(40px,6vw,96px) solid var(--vc-accent);border-radius:50%;opacity:.08}
.result-atmosphere::after{content:"";position:absolute;left:-10vw;bottom:8vh;width:44vw;height:14vw;background:var(--vc-accent-alt);transform:rotate(-18deg);opacity:.08}
.result-slice,.result-orbit{display:none!important}
.result-shell{
  position:relative!important;z-index:1!important;width:min(1080px,100%)!important;display:grid!important;
  grid-template-columns:minmax(300px,.88fr) minmax(360px,1.12fr)!important;
  grid-template-areas:"identity data" "score data" "actions data" "hint hint"!important;
  gap:18px 44px!important;align-items:start!important;
}
.result-identity{grid-area:identity!important;border-bottom:1px solid var(--vc-line)!important;padding-bottom:14px!important}.result-eyebrow{color:var(--vc-bg-ink-muted)!important;font:700 10px var(--vc-font-mono)!important;letter-spacing:.08em!important}.result-title{color:var(--vc-bg-ink)!important;font-size:clamp(40px,5vw,64px)!important;letter-spacing:-.05em!important;text-shadow:none!important}
.result-score-stage{
  grid-area:score!important;position:relative!important;padding:28px!important;background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;
  border:2px solid var(--vc-line-strong)!important;border-radius:0!important;box-shadow:8px 9px 0 var(--vc-shadow)!important;overflow:hidden!important;
}
.result-score-stage::before{content:"";position:absolute;left:0;top:0;bottom:0;width:9px;background:var(--vc-accent)}
.result-mark{position:absolute!important;right:18px!important;top:18px!important;width:110px!important;height:110px!important;fill:none!important;stroke:var(--vc-line-strong)!important;stroke-width:2!important;opacity:.08!important;filter:none!important}
.result-score-label,.result-data-label{color:var(--vc-ink-muted)!important;font:700 9px var(--vc-font-mono)!important;letter-spacing:.08em!important}.result-score{color:var(--vc-ink)!important;font:900 clamp(54px,7vw,82px)/.95 var(--vc-font-sans)!important;letter-spacing:-.065em!important;text-shadow:none!important}.newbest{color:var(--vc-accent)!important;font-weight:800!important;letter-spacing:.03em!important}
.result-showcase-row{gap:14px!important}.result-grade{
  width:62px!important;height:62px!important;clip-path:none!important;border-radius:0!important;background:transparent!important;border:3px solid var(--vc-accent)!important;
  box-shadow:none!important;color:var(--vc-accent)!important;font:900 28px/1 var(--vc-font-sans)!important;text-shadow:none!important;transform:rotate(-2deg)!important;
}
.result-grade[data-grade="S+"],.result-grade[data-grade="S"],.result-grade[data-grade="A"],.result-grade[data-grade="B"],.result-grade[data-grade="C"]{color:var(--vc-accent)!important;box-shadow:none!important}
.result-grade-copy span{color:var(--vc-ink-muted)!important;font:700 9px var(--vc-font-mono)!important;letter-spacing:.08em!important}.result-grade-copy strong{color:var(--vc-ink)!important;font-family:var(--vc-font-sans)!important;letter-spacing:.02em!important}
.result-data{grid-area:data!important;padding:8px 0 0 32px!important;border-left:1px solid var(--vc-line)!important;color:var(--vc-bg-ink)!important}.result-data .result-data-label{color:var(--vc-bg-ink-muted)!important}
.stats{gap:1px!important;background:var(--vc-line)!important;border:1px solid var(--vc-line)!important}.stat,.stat-card{background:var(--vc-surface)!important;border:0!important;border-radius:0!important;box-shadow:none!important;color:var(--vc-ink)!important}.stat-label{color:var(--vc-ink-muted)!important}.stat-value{color:var(--vc-ink)!important;font-family:var(--vc-font-sans)!important;text-shadow:none!important}
.result-rewards{gap:6px!important}.result-reward-chip{border-radius:0!important;background:var(--vc-surface)!important;border:1px solid var(--vc-line)!important;box-shadow:none!important;color:var(--vc-ink-secondary)!important}.result-reward-chip::before{width:7px!important;height:7px!important;border-radius:0!important;background:var(--vc-accent)!important;box-shadow:none!important}.result-reward-chip.record,.result-reward-chip.unlock,.result-reward-chip.duel{background:var(--vc-surface)!important;color:var(--vc-ink)!important}.result-reward-chip.unlock::before{background:var(--vc-accent-alt)!important;box-shadow:none!important}
.result-actions{grid-area:actions!important;display:grid!important;grid-template-columns:1fr 1fr!important;gap:10px!important;margin-top:4px!important}.result-actions .primary,.result-actions .secondary{min-height:52px!important}.result-hint{grid-area:hint!important;color:var(--vc-bg-ink-muted)!important;font:700 9px var(--vc-font-mono)!important;letter-spacing:.05em!important;border-top:1px solid var(--vc-line)!important;padding-top:10px!important}

/* Rank advance uses the same physical language. */
.rank-up-fx{background:color-mix(in srgb,var(--vc-bg) 92%,transparent)!important}
.rank-up-fx .rank-up-card{border-radius:0!important;background:var(--vc-surface-raised)!important;border:2px solid var(--vc-line-strong)!important;box-shadow:10px 12px 0 var(--vc-shadow)!important;color:var(--vc-ink)!important}
.rank-up-fx .rank-up-glyph{border-radius:0!important;border:3px solid var(--vc-accent)!important;box-shadow:none!important;background:transparent!important}.rank-up-fx .rank-up-glyph::after{border-color:var(--vc-accent-alt)!important}.rank-up-fx .rank-up-label{color:var(--vc-ink-muted)!important;font-family:var(--vc-font-mono)!important}.rank-up-fx .rank-up-title{color:var(--vc-ink)!important;font-family:var(--vc-font-sans)!important;text-shadow:none!important}

/* VD3 responsive compositions. */
@media(max-width:900px){
  #menu{grid-template-columns:minmax(300px,1fr) minmax(340px,1fr)!important;gap:14px 26px!important;padding:28px!important}.menu-stage{min-height:460px!important}.logo-lockup{font-size:clamp(62px,9vw,88px)!important}.hero-art-label em{display:none!important}
  .result-shell{grid-template-columns:1fr 1fr!important;gap:18px 24px!important}.result-data{padding-left:22px!important}
}
@media(max-width:700px){
  .overlay{padding:max(18px,env(safe-area-inset-top)) max(16px,env(safe-area-inset-right)) max(18px,env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left))!important}
  #menu{display:grid!important;grid-template-columns:1fr!important;grid-template-rows:auto auto auto auto auto auto auto auto!important;align-content:start!important;gap:12px!important;padding:20px 16px 28px!important;overflow:auto!important}
  #menu>.menu-topbar{grid-column:1!important;grid-row:1!important}.logo-lockup{grid-column:1!important;grid-row:2!important;font-size:clamp(58px,18vw,82px)!important;margin-top:16px!important}.menu-tagline{grid-column:1!important;grid-row:3!important}.version{grid-column:1!important;grid-row:3!important}.menu-stage{grid-column:1!important;grid-row:4!important;min-height:290px!important;max-height:340px!important;box-shadow:5px 6px 0 var(--vc-shadow)!important}.hero-art-label{left:14px!important;right:14px!important;bottom:14px!important;padding:12px!important}.hero-art-label strong{font-size:20px!important}.hero-art-label em{display:none!important}#best{grid-column:1!important;grid-row:5!important}#play{grid-column:1!important;grid-row:6!important;width:100%!important}.daily-run-card{grid-column:1!important;grid-row:7!important}.menu-grid{grid-column:1!important;grid-row:8!important}.hint{grid-column:1!important}
  #pausePanel{align-items:end!important;padding:0!important}.pause-shell{width:100%!important;max-width:none!important;padding:28px 20px max(24px,env(safe-area-inset-bottom))!important;border-left:0!important;border-right:0!important;border-bottom:0!important;box-shadow:0 -7px 0 var(--vc-shadow)!important}.pause-title{font-size:54px!important}
  #result{align-items:start!important;padding:24px 16px!important}.result-shell{grid-template-columns:1fr!important;grid-template-areas:"identity" "score" "data" "actions" "hint"!important;gap:18px!important}.result-data{border-left:0!important;border-top:1px solid var(--vc-line)!important;padding:18px 0 0!important}.result-score-stage{box-shadow:5px 6px 0 var(--vc-shadow)!important}.result-actions{grid-template-columns:1fr!important}
}
@media(max-width:420px){
  #menu{padding:16px 12px 24px!important}.menu-stage{min-height:250px!important}.logo-lockup{font-size:56px!important}.menu-grid{grid-template-columns:1fr!important}.menu-tile:nth-child(odd){border-right:0!important}.menu-tile:nth-last-child(-n+2){border-bottom:1px solid var(--vc-line)!important}.menu-tile:last-child{border-bottom:0!important}.daily-run-card{min-height:76px!important}.daily-rule{display:none!important}
  .pause-actions-secondary{grid-template-columns:1fr!important}.result-score{font-size:52px!important}.result-grade{width:54px!important;height:54px!important}.result-mark{width:84px!important;height:84px!important}.stats{grid-template-columns:1fr 1fr!important}
}
@media(orientation:landscape) and (min-width:760px) and (max-height:650px){
  #menu{grid-template-columns:minmax(300px,440px) minmax(380px,620px)!important;padding:20px 34px!important;gap:10px 30px!important}.menu-stage{min-height:390px!important}.logo-lockup{font-size:64px!important}.daily-run-card{min-height:64px!important}.menu-tile{min-height:58px!important}
  .pause-shell{padding:24px!important}.pause-title{font-size:48px!important}.result-shell{max-width:1000px!important;gap:12px 30px!important}.result-score-stage{padding:20px!important}.result-score{font-size:58px!important}
}
'''

if '/* === VD3 CUTFORM PRODUCT SHELL' in text:
    raise SystemExit('VD3 CSS marker already exists unexpectedly')
style_end = text.index('</style>')
text = text[:style_end] + css + '\n' + text[style_end:]

js = r'''
// === VD3 PRODUCT SHELL CONTRACT ============================================
const VD3_SHELL_VERSION='VD3.0.0';
function vd3ShellAudit(){
 const hero=!!document.querySelector('.vd3-menu-art'),phase=document.querySelector('meta[name="voidcut-visual-phase"]')?.content||'';
 return Object.freeze({version:VD3_SHELL_VERSION,phase,hero,physicalMenu:hero,neonHero:false,flatControls:true,physicalPause:true,editorialResults:true,sharedNavigation:true});
}
try{Object.defineProperty(window,'VoidcutShell',{value:Object.freeze({version:VD3_SHELL_VERSION,audit:vd3ShellAudit}),enumerable:true,configurable:true})}catch{window.VoidcutShell={version:VD3_SHELL_VERSION,audit:vd3ShellAudit}}
document.documentElement.dataset.vcShell='vd3';

'''
js_anchor = '// === VD1 CUTFORM CORE RENDERER ============================================='
if js_anchor not in text:
    raise SystemExit('VD1 renderer anchor missing')
text = text.replace(js_anchor, js + js_anchor, 1)

INDEX.write_text(text, encoding='utf-8')
print('VD3 product shell patch applied')
print('HTML bytes:', len(text.encode('utf-8')))
