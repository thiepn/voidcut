from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
text = INDEX.read_text(encoding='utf-8')

if 'name="voidcut-visual-phase" content="VD6"' in text:
    print('VD6 already applied')
    raise SystemExit(0)
if 'name="voidcut-visual-phase" content="VD5"' not in text:
    raise SystemExit('Expected VD5 baseline')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    text = text.replace(old, new, 1)


def replace_regex(pattern: str, repl: str, label: str) -> None:
    global text
    updated, count = re.subn(pattern, repl, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one regex match, found {count}')
    text = updated


replace_once('name="voidcut-visual-phase" content="VD5"', 'name="voidcut-visual-phase" content="VD6"', 'visual phase')

REPLAY = '''  <div id="replayHud" class="hidden">
    <div class="replay-console vd6-replay-instrument">
      <div class="replay-deck-head">
        <div class="vd6-replay-ident"><span>REPLAY / INSPECT</span><strong id="replayBadge" class="replay-badge">RUN REPLAY</strong></div>
        <div class="replay-highlights" aria-label="Replay highlights"><button id="replayBiggest">BIGGEST</button><button id="replayClosest">CLOSEST</button><button id="replayDeath">DEATH</button></div>
      </div>
      <div class="vd6-replay-readout">
        <div id="replayCutInfo" class="replay-analysis">ANALYZING RUN…</div>
        <div class="replay-time"><span id="replayTimeNow">0:00</span><span>RUN POSITION</span><span id="replayTimeTotal">0:00</span></div>
      </div>
      <div class="replay-timeline vd6-replay-ruler">
        <span id="markerBiggest" class="replay-marker biggest hidden"></span>
        <span id="markerClosest" class="replay-marker closest hidden"></span>
        <span id="markerDeath" class="replay-marker death"></span>
        <input id="replayTimeline" type="range" min="0" max="1000" step="1" value="0" aria-label="Replay timeline">
      </div>
      <div class="vd6-replay-actions">
        <div class="replay-controls">
          <button id="replayPrev">◀ CUT</button>
          <button id="replayPause">PAUSE</button>
          <button id="replaySpeed">1× SPEED</button>
          <button id="replayNext">CUT ▶</button>
        </div>
        <button id="replayExit" class="replay-exit">EXIT REPLAY</button>
      </div>
    </div>
  </div>'''
replace_regex(r'  <div id="replayHud" class="hidden">.*?\n  </div>\n\n\n  <section id="cosmeticsPanel"', REPLAY + '\n\n\n  <section id="cosmeticsPanel"', 'replay console')

SYSTEM_MARKUP = '''  <section id="settingsPanel" class="overlay hidden vd6-utility-screen">
    <header class="screen-hero settings-screen-hero vd6-manual-masthead">
      <div class="screen-hero-copy"><div class="screen-kicker">04 / SYSTEM MANUAL</div><div class="pause-title">SETTINGS</div><div class="screen-subtitle">Controls, presentation, accessibility and device behavior.</div></div>
      <div class="vd6-manual-index" aria-hidden="true"><span>CONFIG</span><strong>04</strong></div>
    </header>
    <div class="settings-list settings-scroll vd6-settings-ledger">
      <section class="settings-group" data-group="audio" data-index="01">
        <div class="settings-group-title"><span class="settings-group-icon" aria-hidden="true"></span><span>AUDIO</span></div>
        <div class="setting"><span class="setting-copy"><b>SFX</b><small>Cuts, impacts and interface sounds</small></span><button class="toggle" data-setting="sound"></button></div>
        <div class="setting"><span class="setting-copy"><b>MUSIC</b><small>Adaptive low-key soundtrack</small></span><button class="toggle" data-setting="music"></button></div>
      </section>
      <section class="settings-group" data-group="controls" data-index="02">
        <div class="settings-group-title"><span class="settings-group-icon" aria-hidden="true"></span><span>CONTROLS</span></div>
        <div class="setting"><span class="setting-copy"><b>HAPTICS</b><small>Vibration feedback on supported devices</small></span><button class="toggle" data-setting="haptics"></button></div>
        <div class="setting"><span class="setting-copy"><b>SWIPE SENSITIVITY</b><small>Minimum drag distance before a cut commits</small></span><button id="swipeSensitivity" class="toggle cycle"></button></div>
      </section>
      <section class="settings-group" data-group="visual" data-index="03">
        <div class="settings-group-title"><span class="settings-group-icon" aria-hidden="true"></span><span>VISUAL</span></div>
        <div class="setting"><span class="setting-copy"><b>MOTION TRACE</b><small>Show the equipped disc trace during play</small></span><button class="toggle" data-setting="trails"></button></div>
        <div class="setting vd6-theme-setting"><span class="setting-copy"><b>THEME</b><small>CUTFORM palette across gameplay and interface</small><span class="vd6-theme-sample" aria-hidden="true"><i></i><i></i><i></i></span></span><button id="colorPalette" class="toggle cycle"></button></div>
        <div class="setting"><span class="setting-copy"><b>TEXTURE</b><small>Printed grain density; stored as a visual preference</small></span><button id="textureMode" class="toggle cycle">FULL</button></div>
        <div class="setting"><span class="setting-copy"><b>LARGE HUD</b><small>Larger gameplay information</small></span><button class="toggle" data-setting="largeUI"></button></div>
      </section>
      <section class="settings-group" data-group="accessibility" data-index="04">
        <div class="settings-group-title"><span class="settings-group-icon" aria-hidden="true"></span><span>ACCESSIBILITY</span></div>
        <div class="setting"><span class="setting-copy"><b>REDUCED MOTION</b><small>Reduces camera movement, separation travel and transitions</small></span><button class="toggle" data-setting="reducedMotion"></button></div>
        <div class="setting"><span class="setting-copy"><b>HIGH CONTRAST</b><small>Strengthens outlines and redundant gameplay cues</small></span><button class="toggle" data-setting="highContrast"></button></div>
      </section>
      <section class="settings-group vd6-system-group" data-group="system" data-index="05">
        <div class="settings-group-title"><span class="settings-group-icon" aria-hidden="true"></span><span>SYSTEM</span></div>
        <div class="setting"><span class="setting-copy"><b>PERFORMANCE</b><small>Auto is recommended for most devices</small></span><button id="powerMode" class="toggle cycle"></button></div>
        <div class="setting"><span class="setting-copy"><b>DISPLAY</b><small>Enter or exit fullscreen</small></span><button id="fullscreenMode" class="toggle cycle">ENTER</button></div>
      </section>
    </div>
    <section class="vd6-utility-actions" aria-label="Help and system tools">
      <div class="vd6-utility-actions-head"><span>HELP & SYSTEM</span><small>These actions do not alter scoring or simulation rules.</small></div>
      <div class="settings-actions"><button id="replayTutorial" class="secondary">PLAY TUTORIAL</button><button id="systemChecks" class="secondary">SYSTEM CHECKS</button></div>
    </section>
    <button id="settingsBack" class="secondary">BACK</button>
  </section>
  <section id="diagnosticsPanel" class="overlay hidden vd6-utility-screen">
    <header class="screen-hero diagnostics-screen-hero vd6-manual-masthead">
      <div class="screen-hero-copy"><div class="screen-kicker">05 / RELEASE INSTRUMENT</div><div class="pause-title">SYSTEM CHECKS</div><div class="screen-subtitle">Installation integrity, storage health and deterministic verification.</div></div>
      <div class="vd6-manual-index" aria-hidden="true"><span>VERIFY</span><strong>05</strong></div>
    </header>
    <div class="vd6-contract-strip" aria-label="Current release contracts">
      <span><small>BUILD</small><b>6.0.0</b></span><span><small>SAVE</small><b>16</b></span><span><small>REPLAY</small><b>8</b></span><span><small>ARENA</small><b>2</b></span><span><small>DIRECTOR</small><b>6</b></span><span><small>DAILY</small><b>1</b></span>
    </div>
    <section class="vd6-report-sheet" aria-labelledby="vd6ReportLabel">
      <div class="vd6-report-head"><span id="vd6ReportLabel">VERIFICATION REPORT</span><small>LOCAL / READ-ONLY UNTIL AN ACTION IS RUN</small></div>
      <pre id="diagnosticsText" class="diag-box" data-status="idle">VERIFY INSTALL TO VERIFY THE INSTALLED RELEASE.</pre>
    </section>
    <section class="vd6-diagnostic-actions" aria-label="Diagnostic actions">
      <div class="vd6-action-label"><span>01 / VERIFY</span><small>Checks the installed release and deterministic runtime.</small></div>
      <button id="runDiagnostics" class="primary">VERIFY INSTALL</button>
      <div class="vd6-action-label"><span>02 / REPORT & DATA</span><small>Portable reports and transactional save tools.</small></div>
      <div class="diag-actions">
        <button id="copyDiagnostics" class="secondary">COPY REPORT</button>
        <button id="runStressDiagnostics" class="secondary">FULL RELEASE CHECK</button>
        <button id="resetMetrics" class="secondary">RESET METRICS</button>
        <button id="exportSave" class="secondary">EXPORT SAVE</button>
        <button id="importSave" class="secondary">IMPORT SAVE</button>
      </div>
    </section>
    <div class="diag-note"><strong>DATA SAFETY</strong><span>Transactional saves keep verified primary, backup and archive generations. Exported save codes are portable and never alter simulation rules or score verification.</span></div>
    <button id="diagnosticsBack" class="secondary">BACK</button>
  </section>

</div>
<div id="orientationNotice"'''
replace_regex(r'  <section id="settingsPanel" class="overlay hidden">.*?</section>\n  <section id="diagnosticsPanel" class="overlay hidden">.*?</section>\n\n</div>\n<div id="orientationNotice"', SYSTEM_MARKUP, 'settings diagnostics markup')

CSS = r'''
/* === VD6 SYSTEM + UTILITY RECONSTRUCTION ================================= */
#settingsPanel,#diagnosticsPanel{
  background:var(--vc-bg)!important;color:var(--vc-bg-ink)!important;
}
#settingsPanel::before,#diagnosticsPanel::before{
  opacity:var(--vc-grain-opacity)!important;background-image:var(--vc-grain-image)!important;background-size:96px 96px!important;mask-image:none!important;
}
#settingsPanel .screen-nav,#diagnosticsPanel .screen-nav{
  background:color-mix(in srgb,var(--vc-bg) 97%,transparent)!important;backdrop-filter:none!important;border-bottom:1px solid var(--vc-line)!important;
}
#settingsPanel .screen-nav .screen-back,#diagnosticsPanel .screen-nav .screen-back{
  min-height:42px!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;box-shadow:var(--vc-shadow-contact)!important;
}
#settingsPanel .screen-nav .screen-nav-brand,#diagnosticsPanel .screen-nav .screen-nav-brand{color:var(--vc-bg-ink-muted)!important;font-family:var(--vc-font-mono)!important}
.vd6-manual-masthead{
  width:min(1180px,100%)!important;min-height:142px!important;margin:0 auto 24px!important;padding:24px 0 22px!important;
  display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;align-items:end!important;gap:28px!important;
  border:0!important;border-bottom:4px solid var(--vc-line-strong)!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;
}
.vd6-manual-masthead::before,.vd6-manual-masthead::after{display:none!important}
.vd6-manual-masthead .screen-kicker{color:var(--vc-bg-ink-muted)!important;font:700 10px/1 var(--vc-font-mono)!important;letter-spacing:.14em!important}
.vd6-manual-masthead .pause-title{margin-top:8px!important;color:var(--vc-bg-ink)!important;font:700 clamp(42px,5vw,68px)/.9 var(--vc-font-sans)!important;letter-spacing:-.055em!important;text-transform:uppercase!important}
.vd6-manual-masthead .screen-subtitle{max-width:680px!important;margin-top:12px!important;color:var(--vc-bg-ink-muted)!important;font:500 14px/1.45 var(--vc-font-sans)!important;letter-spacing:0!important;text-transform:none!important}
.vd6-manual-index{display:grid;justify-items:end;align-content:end;min-width:96px;color:var(--vc-bg-ink)!important}.vd6-manual-index span{font:700 9px/1 var(--vc-font-mono);letter-spacing:.14em;color:var(--vc-bg-ink-muted)}.vd6-manual-index strong{font:700 74px/.72 var(--vc-font-sans);letter-spacing:-.08em}

/* Settings is a manual/ledger, not a card dashboard. */
.vd6-settings-ledger{width:min(1180px,100%)!important;margin:0 auto!important;display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:0!important;border-top:1px solid var(--vc-line)!important;border-left:1px solid var(--vc-line)!important}
#settingsPanel .settings-group{position:relative!important;margin:0!important;padding:0!important;border:0!important;border-right:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important;border-radius:0!important;background:var(--vc-surface)!important;box-shadow:none!important;color:var(--vc-ink)!important}
#settingsPanel .settings-group[data-group="system"]{grid-column:1/-1!important;display:grid!important;grid-template-columns:1fr 1fr!important}.vd6-system-group .settings-group-title{grid-column:1/-1!important}
#settingsPanel .settings-group-title{position:relative!important;min-height:56px!important;margin:0!important;padding:14px 16px 12px 58px!important;display:flex!important;align-items:center!important;border:0!important;border-bottom:2px solid var(--vc-line-strong)!important;color:var(--vc-ink)!important;font:700 13px/1 var(--vc-font-sans)!important;letter-spacing:.03em!important}
#settingsPanel .settings-group-title::before{content:attr(data-unused);display:none}.settings-group[data-index] .settings-group-title::after{content:attr(data-index)}
#settingsPanel .settings-group[data-index]::before{content:attr(data-index);position:absolute;left:14px;top:16px;z-index:2;color:var(--vc-accent)!important;font:700 10px/1 var(--vc-font-mono);letter-spacing:.08em}
#settingsPanel .settings-group-icon{display:none!important}
#settingsPanel .setting{min-height:78px!important;padding:13px 16px!important;display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;align-items:center!important;gap:18px!important;border:0!important;border-bottom:1px solid var(--vc-line)!important;background:transparent!important}
#settingsPanel .setting:last-child{border-bottom:0!important}
#settingsPanel .setting-copy b{display:block!important;color:var(--vc-ink)!important;font:700 13px/1.1 var(--vc-font-sans)!important;letter-spacing:.015em!important}
#settingsPanel .setting-copy small{display:block!important;margin-top:5px!important;color:var(--vc-ink-muted)!important;font:500 11px/1.35 var(--vc-font-sans)!important}
#settingsPanel .toggle{min-width:82px!important;width:auto!important;min-height:38px!important;padding:0 12px!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;box-shadow:2px 3px 0 var(--vc-shadow)!important;font:700 10px/1 var(--vc-font-mono)!important;letter-spacing:.06em!important}
#settingsPanel .toggle.is-on{background:var(--vc-accent)!important;border-color:var(--vc-accent)!important;color:var(--vc-on-accent)!important}
#settingsPanel .toggle.cycle{min-width:108px!important}.vd6-theme-setting .toggle.cycle{min-width:116px!important}
#settingsPanel .toggle:active{transform:translate(2px,3px)!important;box-shadow:none!important}
.vd6-theme-sample{display:flex!important;width:70px;height:16px;margin-top:8px!important;border:1px solid var(--vc-line)!important;overflow:hidden}.vd6-theme-sample i{display:block;flex:1}.vd6-theme-sample i:nth-child(1){background:var(--vc-bg-alt)}.vd6-theme-sample i:nth-child(2){background:var(--vc-accent)}.vd6-theme-sample i:nth-child(3){background:var(--vc-accent-alt)}
.vd6-utility-actions{width:min(1180px,100%)!important;margin:22px auto 0!important;padding:0!important;border-top:4px solid var(--vc-bg-ink)!important;color:var(--vc-bg-ink)!important}.vd6-utility-actions-head{display:flex;justify-content:space-between;gap:18px;padding:12px 0;border-bottom:1px solid var(--vc-line)!important}.vd6-utility-actions-head span{font:700 13px var(--vc-font-sans)}.vd6-utility-actions-head small{color:var(--vc-bg-ink-muted)!important;font:500 11px var(--vc-font-sans)}
#settingsPanel .settings-actions{display:grid!important;grid-template-columns:1fr 1fr!important;gap:0!important;margin:0!important;border-left:1px solid var(--vc-line)!important}
#settingsPanel .settings-actions .secondary{min-height:52px!important;border:0!important;border-right:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important;border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;box-shadow:none!important}
#settingsPanel>#settingsBack,#diagnosticsPanel>#diagnosticsBack{display:none!important}

/* Diagnostics is a release instrument with a paper contract strip and one report surface. */
.vd6-contract-strip{width:min(1180px,100%)!important;margin:0 auto 18px!important;display:grid!important;grid-template-columns:repeat(6,1fr)!important;border-top:1px solid var(--vc-line)!important;border-left:1px solid var(--vc-line)!important}
.vd6-contract-strip>span{min-height:62px;padding:10px 12px;border-right:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important}.vd6-contract-strip small{display:block;color:var(--vc-ink-muted)!important;font:700 8px/1 var(--vc-font-mono);letter-spacing:.10em}.vd6-contract-strip b{display:block;margin-top:6px;font:700 18px/1 var(--vc-font-sans)}
.vd6-report-sheet{width:min(1180px,100%)!important;margin:0 auto!important;border:2px solid var(--vc-line-strong)!important;background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;box-shadow:5px 6px 0 var(--vc-shadow)!important}.vd6-report-head{display:flex;justify-content:space-between;gap:18px;padding:11px 14px;border-bottom:1px solid var(--vc-line)!important}.vd6-report-head span{font:700 11px var(--vc-font-sans)}.vd6-report-head small{color:var(--vc-ink-muted)!important;font:700 8px var(--vc-font-mono);letter-spacing:.08em}
#diagnosticsPanel .diag-box{min-height:270px!important;max-height:46vh!important;margin:0!important;padding:18px!important;overflow:auto!important;border:0!important;border-radius:0!important;background:var(--vc-substrate)!important;color:var(--vc-on-substrate)!important;box-shadow:none!important;font:500 11px/1.62 var(--vc-font-mono)!important;white-space:pre-wrap!important;word-break:break-word!important;tab-size:2!important}
#diagnosticsPanel .diag-box[data-status="pass"]{box-shadow:inset 5px 0 var(--vc-success)!important}#diagnosticsPanel .diag-box[data-status="fail"]{box-shadow:inset 5px 0 var(--vc-danger)!important}
.vd6-diagnostic-actions{width:min(1180px,100%)!important;margin:24px auto 0!important;border-top:4px solid var(--vc-bg-ink)!important}.vd6-action-label{display:flex!important;justify-content:space-between!important;gap:18px!important;padding:11px 0!important;border-bottom:1px solid var(--vc-line)!important;color:var(--vc-bg-ink)!important}.vd6-action-label span{font:700 11px var(--vc-font-mono);letter-spacing:.08em}.vd6-action-label small{color:var(--vc-bg-ink-muted)!important;font:500 11px var(--vc-font-sans)}
#diagnosticsPanel #runDiagnostics{width:100%!important;min-height:60px!important;margin:0!important;border:0!important;border-radius:0!important;background:var(--vc-accent)!important;color:var(--vc-on-accent)!important;box-shadow:none!important;font:700 16px var(--vc-font-sans)!important;letter-spacing:.02em!important}
#diagnosticsPanel .diag-actions{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:0!important;margin:0!important;border-left:1px solid var(--vc-line)!important}.diag-actions .secondary{min-height:56px!important;padding:8px 10px!important;border:0!important;border-right:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important;border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;box-shadow:none!important;font-size:10px!important}
#diagnosticsPanel .diag-note{width:min(1180px,100%)!important;margin:16px auto 0!important;padding:12px 14px!important;display:grid!important;grid-template-columns:auto 1fr!important;gap:14px!important;border:1px solid var(--vc-line)!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;color:var(--vc-bg-ink-muted)!important}.diag-note strong{color:var(--vc-bg-ink)!important;font:700 9px var(--vc-font-mono);letter-spacing:.10em}.diag-note span{font:500 11px/1.4 var(--vc-font-sans)}

/* Replay is an inspection ruler, intentionally subordinate to the playfield. */
#replayHud{position:fixed!important;inset:0!important;z-index:120!important;pointer-events:none!important}.vd6-replay-instrument{pointer-events:auto!important;position:absolute!important;left:50%!important;bottom:max(14px,env(safe-area-inset-bottom))!important;transform:translateX(-50%)!important;width:min(980px,calc(100vw - 28px))!important;padding:0!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;box-shadow:6px 7px 0 var(--vc-shadow)!important;backdrop-filter:none!important}
.vd6-replay-instrument .replay-deck-head{min-height:54px!important;padding:8px 10px 8px 14px!important;display:flex!important;align-items:center!important;justify-content:space-between!important;gap:16px!important;border-bottom:1px solid var(--vc-line)!important}.vd6-replay-ident{display:grid!important;gap:3px!important}.vd6-replay-ident>span{color:var(--vc-ink-muted)!important;font:700 8px/1 var(--vc-font-mono)!important;letter-spacing:.12em!important}.vd6-replay-ident .replay-badge{color:var(--vc-ink)!important;font:700 14px/1 var(--vc-font-sans)!important;letter-spacing:.02em!important}
.vd6-replay-instrument .replay-highlights{display:grid!important;grid-template-columns:repeat(3,auto)!important;gap:1px!important;background:var(--vc-line)!important;border:1px solid var(--vc-line)!important}.vd6-replay-instrument .replay-highlights button{min-height:34px!important;padding:0 10px!important;border:0!important;border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-ink-secondary)!important;box-shadow:none!important;font:700 8px var(--vc-font-mono)!important;letter-spacing:.05em!important}
.vd6-replay-readout{display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;gap:14px!important;padding:10px 14px!important;border-bottom:1px solid var(--vc-line)!important}.vd6-replay-instrument .replay-analysis{min-height:32px!important;color:var(--vc-ink-secondary)!important;font:500 10px/1.45 var(--vc-font-mono)!important}.vd6-replay-instrument .replay-analysis .accent{color:var(--vc-accent)!important}.vd6-replay-instrument .replay-analysis .muted{color:var(--vc-ink-muted)!important}.vd6-replay-instrument .replay-time{min-width:190px!important;display:grid!important;grid-template-columns:auto auto!important;grid-template-rows:auto auto!important;align-items:end!important;gap:1px 10px!important;color:var(--vc-ink)!important;font:700 11px var(--vc-font-mono)!important}.vd6-replay-instrument .replay-time span:nth-child(2){grid-column:1/-1!important;grid-row:1!important;color:var(--vc-ink-muted)!important;font-size:7px!important;letter-spacing:.10em!important}.vd6-replay-instrument .replay-time span:nth-child(1){grid-column:1!important;grid-row:2!important}.vd6-replay-instrument .replay-time span:nth-child(3){grid-column:2!important;grid-row:2!important;text-align:right!important}
.vd6-replay-ruler{position:relative!important;height:42px!important;margin:0!important;padding:0 14px!important;display:flex!important;align-items:center!important;background:repeating-linear-gradient(90deg,transparent 0 23px,color-mix(in srgb,var(--vc-line) 60%,transparent) 23px 24px)!important;border-bottom:1px solid var(--vc-line)!important}.vd6-replay-ruler input[type="range"]{width:100%!important;accent-color:var(--vc-accent)!important}.vd6-replay-instrument .replay-marker{top:3px!important;width:2px!important;height:11px!important;border:0!important;border-radius:0!important;background:var(--vc-accent-alt)!important;box-shadow:none!important}.vd6-replay-instrument .replay-marker.death{background:var(--vc-danger)!important}.vd6-replay-instrument .replay-marker.biggest{background:var(--vc-accent)!important}
.vd6-replay-actions{display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;gap:0!important}.vd6-replay-instrument .replay-controls{display:grid!important;grid-template-columns:repeat(4,1fr)!important;gap:0!important;border-left:1px solid var(--vc-line)!important}.vd6-replay-instrument .replay-controls button,.vd6-replay-instrument .replay-exit{min-height:44px!important;border:0!important;border-right:1px solid var(--vc-line)!important;border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-ink)!important;box-shadow:none!important;font:700 9px var(--vc-font-mono)!important}.vd6-replay-instrument .replay-exit{min-width:130px!important;border-right:0!important;border-left:2px solid var(--vc-danger)!important;color:var(--vc-danger)!important}

/* Utility warnings and short-lived system states use the same physical grammar. */
.orientation-notice,#orientationNotice{border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;box-shadow:5px 6px 0 var(--vc-shadow)!important;backdrop-filter:none!important}.orientation-notice strong{color:var(--vc-danger)!important;font-family:var(--vc-font-sans)!important}.orientation-notice span{color:var(--vc-ink-muted)!important}
.health-note{border-radius:0!important;background:var(--vc-surface)!important;color:var(--vc-danger)!important;border:1px solid var(--vc-danger)!important;box-shadow:none!important;text-shadow:none!important}.short-swipe{border-radius:0!important;background:var(--vc-surface-raised)!important;color:var(--vc-danger)!important;border:2px solid var(--vc-danger)!important;box-shadow:2px 3px 0 var(--vc-shadow)!important;text-shadow:none!important;font-family:var(--vc-font-mono)!important}
#coach,.coach{border-radius:0!important;background:var(--vc-surface-raised)!important;color:var(--vc-ink)!important;border:2px solid var(--vc-line-strong)!important;box-shadow:4px 5px 0 var(--vc-shadow)!important;backdrop-filter:none!important;text-shadow:none!important}

@media(max-width:760px){
 .vd6-manual-masthead{min-height:108px!important;margin-bottom:14px!important;padding:14px 0 16px!important;border-bottom-width:3px!important}.vd6-manual-masthead .pause-title{font-size:40px!important}.vd6-manual-index strong{font-size:54px!important}.vd6-manual-index{min-width:68px!important}
 .vd6-settings-ledger{grid-template-columns:1fr!important}.vd6-system-group{grid-column:1!important;grid-template-columns:1fr!important}.vd6-system-group .settings-group-title{grid-column:1!important}
 #settingsPanel .setting{min-height:72px!important;padding:12px 13px!important}.vd6-utility-actions-head,.vd6-action-label{display:grid!important;gap:4px!important}.vd6-utility-actions-head small,.vd6-action-label small{font-size:10px!important}
 .vd6-contract-strip{grid-template-columns:repeat(3,1fr)!important}.vd6-report-sheet{box-shadow:4px 5px 0 var(--vc-shadow)!important}#diagnosticsPanel .diag-box{min-height:230px!important;max-height:42vh!important;padding:14px!important;font-size:10px!important}.diag-actions{grid-template-columns:repeat(2,1fr)!important}.diag-actions .secondary:last-child{grid-column:1/-1!important}
 .vd6-replay-instrument{width:calc(100vw - 14px)!important;bottom:max(7px,env(safe-area-inset-bottom))!important;box-shadow:4px 5px 0 var(--vc-shadow)!important}.vd6-replay-readout{grid-template-columns:1fr!important}.vd6-replay-instrument .replay-time{min-width:0!important;width:100%!important}.vd6-replay-instrument .replay-highlights button{padding:0 7px!important}.vd6-replay-instrument .replay-controls button{font-size:8px!important;padding:0 3px!important}.vd6-replay-instrument .replay-exit{min-width:96px!important;font-size:8px!important}
}
@media(max-width:420px){
 .vd6-manual-index span{display:none!important}.vd6-manual-index strong{font-size:48px!important}.vd6-manual-masthead .screen-subtitle{font-size:12px!important}.vd6-contract-strip>span{min-height:54px!important;padding:8px!important}.vd6-contract-strip b{font-size:16px!important}
 #settingsPanel .setting{grid-template-columns:minmax(0,1fr) auto!important;gap:10px!important}#settingsPanel .toggle{min-width:74px!important;padding:0 8px!important}#settingsPanel .toggle.cycle{min-width:94px!important}.vd6-theme-sample{width:58px!important}
 .vd6-replay-instrument .replay-deck-head{align-items:start!important}.vd6-replay-instrument .replay-highlights{grid-template-columns:1fr!important}.vd6-replay-instrument .replay-highlights button{min-height:25px!important}.vd6-replay-actions{grid-template-columns:1fr!important}.vd6-replay-instrument .replay-exit{min-height:38px!important;border-left:0!important;border-top:2px solid var(--vc-danger)!important}
}
@media(orientation:landscape) and (min-width:760px) and (max-height:620px){
 .vd6-manual-masthead{min-height:68px!important;margin-bottom:9px!important;padding:6px 0 9px!important;border-bottom-width:2px!important}.vd6-manual-masthead .pause-title{font-size:30px!important}.vd6-manual-masthead .screen-subtitle{display:none!important}.vd6-manual-index strong{font-size:38px!important}
 .vd6-settings-ledger{grid-template-columns:repeat(3,1fr)!important}.vd6-system-group{grid-column:auto!important;display:block!important}#settingsPanel .setting{min-height:50px!important;padding:8px 10px!important}.setting-copy small{display:none!important}.vd6-utility-actions{margin-top:10px!important}
 #diagnosticsPanel .diag-box{min-height:150px!important;max-height:34vh!important}.vd6-contract-strip{margin-bottom:8px!important}.vd6-diagnostic-actions{margin-top:10px!important}.vd6-action-label{padding:6px 0!important}.diag-actions .secondary{min-height:40px!important}
 .vd6-replay-instrument{width:min(1100px,calc(100vw - 20px))!important}.vd6-replay-readout{padding:6px 10px!important}.vd6-replay-ruler{height:32px!important}.vd6-replay-instrument .replay-controls button,.vd6-replay-instrument .replay-exit{min-height:36px!important}
}
body.high-contrast #settingsPanel .settings-group,body.high-contrast .vd6-report-sheet,body.high-contrast .vd6-replay-instrument{border-color:#fff!important;box-shadow:none!important}
body:has(.toggle[data-setting="reducedMotion"].is-on) .vd6-replay-instrument{transition:none!important}
'''
replace_once('</style>', CSS + '\n</style>', 'VD6 CSS')

JS = r'''
// === VD6 SYSTEM + UTILITY CONTRACT ========================================
const VD6_SYSTEM_VERSION='VD6.0.0';
const VD6_THEME_MAP=Object.freeze({arcade:'paper',sunset:'carbon',ion:'cobalt',ice:'kelp',vector:'plum',spectrum:'mono'});
const VD6_THEME_LABELS=Object.freeze({paper:'PAPER',carbon:'CARBON',cobalt:'COBALT',kelp:'KELP',plum:'PLUM',mono:'MONO'});
const VD6_TEXTURE_ORDER=Object.freeze(['full','reduced','off']);
function vd6ThemeForSetting(id){return VD6_THEME_MAP[id]||'paper'}
function vd6ApplyThemeFromSetting(){const theme=vd6ThemeForSetting(save?.settings?.colorTheme);try{window.VoidcutDesign?.applyTheme(theme,{persist:true})}catch{}document.body.dataset.vd6Theme=theme;return theme}
function vd6RenderUtilityPreferences(){const theme=vd6ApplyThemeFromSetting(),palette=$('colorPalette'),texture=$('textureMode');if(palette){palette.textContent=VD6_THEME_LABELS[theme]||theme.toUpperCase();palette.setAttribute('aria-label',`Theme: ${VD6_THEME_LABELS[theme]||theme}`)}if(texture){const mode=window.VoidcutDesign?.getTextureMode?.()||'full';texture.textContent=mode.toUpperCase();texture.setAttribute('aria-label',`Texture: ${mode}`)}}
function vd6CycleTheme(){const ids=availablePaletteIds(save);if(!ids.length)return;const current=ids.includes(save.settings.colorTheme)?save.settings.colorTheme:ids[0],index=Math.max(0,ids.indexOf(current)),next=ids[(index+1)%ids.length];save.settings.colorTheme=next;applyUiPalette();vd6ApplyThemeFromSetting();persist();vd6RenderUtilityPreferences();uiSound('tap')}
function vd6CycleTexture(){const api=window.VoidcutDesign;if(!api?.getTextureMode||!api?.setTextureMode)return;const current=api.getTextureMode(),index=Math.max(0,VD6_TEXTURE_ORDER.indexOf(current)),next=VD6_TEXTURE_ORDER[(index+1)%VD6_TEXTURE_ORDER.length];api.setTextureMode(next);vd6RenderUtilityPreferences();uiSound('tap')}
function vd6BindUtilityControls(){const palette=$('colorPalette'),texture=$('textureMode');if(palette)palette.onclick=vd6CycleTheme;if(texture)texture.onclick=vd6CycleTexture}
function vd6SyncDiagnosticState(){const box=$('diagnosticsText');if(!box)return;const t=(box.textContent||'').toUpperCase();let status='idle';if(/(?:OVERALL|RESULT|STATUS)\s*[:=-]\s*(?:FAIL|FAILED|ERROR)/.test(t)||/VERIFICATION FAILED/.test(t))status='fail';else if(/(?:OVERALL|RESULT|STATUS)\s*[:=-]\s*(?:PASS|PASSED|OK)/.test(t)||/INSTALL VERIFIED/.test(t))status='pass';box.dataset.status=status}
let vd6DiagObserver=null;
function vd6InitUtilityLayer(){vd6BindUtilityControls();vd6RenderUtilityPreferences();vd6SyncDiagnosticState();const box=$('diagnosticsText');if(box&&typeof MutationObserver!=='undefined'&&!vd6DiagObserver){vd6DiagObserver=new MutationObserver(vd6SyncDiagnosticState);vd6DiagObserver.observe(box,{childList:true,characterData:true,subtree:true})}document.addEventListener('voidcut:themechange',vd6RenderUtilityPreferences);document.addEventListener('voidcut:texturechange',vd6RenderUtilityPreferences)}
const vd6BaseRenderToggles=renderToggles;
renderToggles=function(...args){const result=vd6BaseRenderToggles(...args);vd6BindUtilityControls();vd6RenderUtilityPreferences();return result};
function vd6UtilityAudit(){const settings=document.getElementById('settingsPanel'),diagnostics=document.getElementById('diagnosticsPanel'),replay=document.getElementById('replayHud'),api=window.VoidcutDesign;const theme=vd6ThemeForSetting(save?.settings?.colorTheme);return Object.freeze({version:VD6_SYSTEM_VERSION,phase:document.querySelector('meta[name="voidcut-visual-phase"]')?.content||'',manualSettings:!!settings?.querySelector('.vd6-settings-ledger'),themeBridge:api?.getTheme?.()===theme,textureControl:!!document.getElementById('textureMode'),releaseInstrument:!!diagnostics?.querySelector('.vd6-report-sheet'),replayInstrument:!!replay?.querySelector('.vd6-replay-instrument'),legacyNeonCopy:settings?.textContent?.toLowerCase().includes('neon')||false,contracts:{build:RELEASE_VERSION,save:SAVE_SCHEMA,replay:RELEASE_CONTRACT.replay,arena:RELEASE_CONTRACT.arena,director:RELEASE_CONTRACT.director,daily:RELEASE_CONTRACT.daily}})}
Object.defineProperty(window,'VoidcutUtilities',{value:Object.freeze({version:VD6_SYSTEM_VERSION,themeMap:VD6_THEME_MAP,applyTheme:vd6ApplyThemeFromSetting,render:vd6RenderUtilityPreferences,audit:vd6UtilityAudit}),enumerable:true,configurable:false,writable:false});
'''
replace_once('// === V6.0 VISUAL RELEASE =============================================', JS + '\n\n// === V6.0 VISUAL RELEASE =============================================', 'VD6 JS contract')
replace_once('applyUiProductionPolish();renderToggles();applyAccessibilityClasses();renderCosmetics();showMenu();', 'applyUiProductionPolish();renderToggles();applyAccessibilityClasses();vd6InitUtilityLayer();renderCosmetics();showMenu();', 'VD6 boot')

INDEX.write_text(text, encoding='utf-8')
print('VD6 system + utility reconstruction applied')
print('HTML bytes:', len(text.encode('utf-8')))
