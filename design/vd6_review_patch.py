from pathlib import Path

p=Path(__file__).resolve().parents[1]/'index.html'
text=p.read_text(encoding='utf-8')
if '/* === VD6 CERTIFICATION CORRECTIONS' in text:
    print('VD6 certification corrections already present')
    raise SystemExit(0)
if 'name="voidcut-visual-phase" content="VD6"' not in text:
    raise SystemExit('Expected VD6 baseline')

# Remove a redundant pseudo-index rule; the group-level index is the actual owner.
text=text.replace("#settingsPanel .settings-group-title::before{content:attr(data-unused);display:none}.settings-group[data-index] .settings-group-title::after{content:attr(data-index)}\n", "")

# Diagnostics already owns pass/warn/fail classes. Keep data-status as a supplemental audit signal,
# but make the canonical runtime classes visually authoritative too.
needle="#diagnosticsPanel .diag-box[data-status=\"pass\"]{box-shadow:inset 5px 0 var(--vc-success)!important}#diagnosticsPanel .diag-box[data-status=\"fail\"]{box-shadow:inset 5px 0 var(--vc-danger)!important}\n"
replacement=needle + "#diagnosticsPanel .diag-box.pass,#diagnosticsPanel .diag-box[data-status=\"pass\"]{box-shadow:inset 5px 0 var(--vc-success)!important}#diagnosticsPanel .diag-box.warn{box-shadow:inset 5px 0 var(--vc-accent-alt)!important}#diagnosticsPanel .diag-box.fail,#diagnosticsPanel .diag-box[data-status=\"fail\"]{box-shadow:inset 5px 0 var(--vc-danger)!important}\n"
if needle not in text: raise SystemExit('Diagnostics status CSS anchor missing')
text=text.replace(needle,replacement,1)

# Teach the supplemental status observer about WARN as well.
old="if(/(?:OVERALL|RESULT|STATUS)\\s*[:=-]\\s*(?:FAIL|FAILED|ERROR)/.test(t)||/VERIFICATION FAILED/.test(t))status='fail';else if(/(?:OVERALL|RESULT|STATUS)\\s*[:=-]\\s*(?:PASS|PASSED|OK)/.test(t)||/INSTALL VERIFIED/.test(t))status='pass';box.dataset.status=status"
new="if(/(?:OVERALL|RESULT|STATUS)\\s*[:=-]\\s*(?:FAIL|FAILED|ERROR)/.test(t)||/VERIFICATION FAILED/.test(t))status='fail';else if(/(?:OVERALL|RESULT|STATUS)\\s*[:=-]\\s*WARN/.test(t))status='warn';else if(/(?:OVERALL|RESULT|STATUS)\\s*[:=-]\\s*(?:PASS|PASSED|OK)/.test(t)||/INSTALL VERIFIED/.test(t))status='pass';box.dataset.status=status"
if old not in text: raise SystemExit('Diagnostic observer anchor missing')
text=text.replace(old,new,1)

# Update technical report language to the reconstructed presentation identity only.
old_report="`PRESENTATION: ${RELEASE_NAME} • SHOWCASE VFX + ADAPTIVE AUDIO • tier ${performanceTier()} • ${presentationFps()?presentationFps()+' FPS cap':'native refresh'} • adaptive budget ${feedbackBudget().toFixed(2)} • reduced motion ${save.settings.reducedMotion?'ON':'OFF'}`"
new_report="`PRESENTATION: ${RELEASE_NAME} • CUTFORM PHYSICAL GRAPHICS + ADAPTIVE AUDIO • tier ${performanceTier()} • ${presentationFps()?presentationFps()+' FPS cap':'native refresh'} • adaptive budget ${feedbackBudget().toFixed(2)} • reduced motion ${save.settings.reducedMotion?'ON':'OFF'}`"
if old_report not in text: raise SystemExit('Presentation report anchor missing')
text=text.replace(old_report,new_report,1)

# Certification marker is deliberately tiny and late so it wins legacy utility CSS.
marker='''\n/* === VD6 CERTIFICATION CORRECTIONS ======================================= */\n#diagnosticsPanel .diag-box[data-status="warn"]{box-shadow:inset 5px 0 var(--vc-accent-alt)!important}\n@media(max-width:420px){.vd6-report-head small{display:none!important}.vd6-replay-ident>span{font-size:7px!important}}\n'''
text=text.replace('</style>',marker+'\n</style>',1)
p.write_text(text,encoding='utf-8')
print('VD6 certification corrections applied')
