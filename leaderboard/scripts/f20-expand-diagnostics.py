from pathlib import Path

root = Path(__file__).resolve().parents[2]
index_path = root / 'index.html'
sw_path = root / 'sw.js'
register_path = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'
f3_test_path = root / 'leaderboard' / 'scripts' / 'test-ranked-timing-source.mjs'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

html = index_path.read_text(encoding='utf-8')

# Allow diagnostics to exercise the real timing guards without surfacing a
# synthetic in-game warning. Normal runtime call sites omit the new argument,
# so their notify=true behavior is unchanged.
html = replace_once(
    html,
    "function trackRankedFrameGap(rawSec,simBudget){if(!rankedTimingActive()||!rankedTimingIntegrity)return;const wall=Math.max(0,Number(rawSec)||0),budget=Math.max(0,Number(simBudget)||0),discarded=Math.max(0,wall-budget);rankedTimingIntegrity.wallSeconds+=wall;rankedTimingIntegrity.simBudgetSeconds+=budget;rankedTimingIntegrity.discardedSeconds+=discarded;if(wall>RANKED_MAX_SINGLE_FRAME_GAP){invalidateRankedTiming('FRAME STALL');return}if(rankedTimingIntegrity.discardedSeconds>=RANKED_MAX_DISCARDED_TIME)invalidateRankedTiming('TIMING DRIFT')}",
    "function trackRankedFrameGap(rawSec,simBudget,notify=true){if(!rankedTimingActive()||!rankedTimingIntegrity)return;const wall=Math.max(0,Number(rawSec)||0),budget=Math.max(0,Number(simBudget)||0),discarded=Math.max(0,wall-budget);rankedTimingIntegrity.wallSeconds+=wall;rankedTimingIntegrity.simBudgetSeconds+=budget;rankedTimingIntegrity.discardedSeconds+=discarded;if(wall>RANKED_MAX_SINGLE_FRAME_GAP){invalidateRankedTiming('FRAME STALL',notify);return}if(rankedTimingIntegrity.discardedSeconds>=RANKED_MAX_DISCARDED_TIME)invalidateRankedTiming('TIMING DRIFT',notify)}",
    'ranked frame-gap diagnostic notify control',
)
html = replace_once(
    html,
    "function trackRankedCatchup(stepLimitHit){if(!stepLimitHit||!rankedTimingActive()||!rankedTimingIntegrity)return;rankedTimingIntegrity.stepLimitHits++;invalidateRankedTiming('CATCH-UP LIMIT')}",
    "function trackRankedCatchup(stepLimitHit,notify=true){if(!stepLimitHit||!rankedTimingActive()||!rankedTimingIntegrity)return;rankedTimingIntegrity.stepLimitHits++;invalidateRankedTiming('CATCH-UP LIMIT',notify)}",
    'ranked catch-up diagnostic notify control',
)

helpers = r'''function diagnosticRankedTimingProbe(){const snapshot={state,paused,transition,tutorialMode,activeLeaderboardTicket,rankedRunInvalidReason,rankedRunInvalidNoticeShown,rankedTimingIntegrity,last,acc},fresh=()=>{state='play';paused=false;transition=false;tutorialMode=false;activeLeaderboardTicket={ticketId:'diagnostic'};rankedRunInvalidReason=null;rankedRunInvalidNoticeShown=false;resetRankedTimingIntegrity()};try{fresh();trackRankedFrameGap(.12,.05,false);if(!activeLeaderboardTicket||Math.abs(rankedTimingIntegrity.discardedSeconds-.07)>.000001)throw new Error('safe-frame accounting');fresh();trackRankedFrameGap(.21,.05,false);if(activeLeaderboardTicket||rankedRunInvalidReason!=='FRAME STALL')throw new Error('frame-stall guard');fresh();for(let i=0;i<6;i++)trackRankedFrameGap(.10,.05,false);if(activeLeaderboardTicket||rankedRunInvalidReason!=='TIMING DRIFT')throw new Error('timing-drift guard');fresh();trackRankedCatchup(true,false);if(activeLeaderboardTicket||rankedRunInvalidReason!=='CATCH-UP LIMIT'||rankedTimingIntegrity.stepLimitHits!==1)throw new Error('catch-up guard');fresh();last=1000;acc=.005;trackRankedTimingReset('DIAGNOSTIC RESET',false,1100);if(!activeLeaderboardTicket||rankedTimingIntegrity.timingResets!==1)throw new Error('safe reset accounting');last=1100;acc=.005;trackRankedTimingReset('DIAGNOSTIC RESET',false,1250);if(activeLeaderboardTicket||rankedRunInvalidReason!=='DIAGNOSTIC RESET'||rankedTimingIntegrity.timingResets!==2)throw new Error('reset drift guard');return{status:'PASS',summary:'FRAME STALL • DRIFT • CATCH-UP • RESET GUARDS PASS'}}catch(err){return{status:'FAIL',summary:`${String(err?.message||'TIMING PROBE FAILED').toUpperCase()}`}}finally{state=snapshot.state;paused=snapshot.paused;transition=snapshot.transition;tutorialMode=snapshot.tutorialMode;activeLeaderboardTicket=snapshot.activeLeaderboardTicket;rankedRunInvalidReason=snapshot.rankedRunInvalidReason;rankedRunInvalidNoticeShown=snapshot.rankedRunInvalidNoticeShown;rankedTimingIntegrity=snapshot.rankedTimingIntegrity;last=snapshot.last;acc=snapshot.acc}}
async function diagnosticLeaderboardProbe(){try{const data=await leaderboardRequest('/leaderboard?limit=5',{},false);if(!data||!Array.isArray(data.rows))return{status:'FAIL',summary:'MALFORMED LEADERBOARD RESPONSE'};const rules=data.ruleset||{};if(rules.replay!==RELEASE_CONTRACT.replay||rules.arena!==RELEASE_CONTRACT.arena||rules.director!==RELEASE_CONTRACT.director)return{status:'FAIL',summary:'LEADERBOARD RULESET MISMATCH'};for(const row of data.rows){if(!Number.isInteger(row?.rank)||row.rank<1||typeof row?.name!=='string'||!Number.isFinite(Number(row?.score))||!Number.isFinite(Number(row?.chamber)))return{status:'FAIL',summary:'MALFORMED LEADERBOARD ROW'};if(row.replayHash!=null&&row.replayHash!==''&&!/^[a-f0-9]{64}$/i.test(String(row.replayHash)))return{status:'FAIL',summary:'MALFORMED LEADERBOARD REPLAY HASH'}}const target=data.rows.find(row=>/^[a-f0-9]{64}$/i.test(String(row?.replayHash||'')));if(!target)return{status:'WARN',summary:`API PASS • ${data.rows.length} ROW${data.rows.length===1?'':'S'} • NO REPLAY TO VERIFY`};const hash=String(target.replayHash).toLowerCase(),replay=await leaderboardRequest(`/replay/${encodeURIComponent(hash)}`,{},false);if(!validReplay(replay)||!verifyCompetitiveReplay(replay)||String(replay.hash||'').toLowerCase()!==hash)return{status:'FAIL',summary:'LIVE REPLAY RETRIEVAL / LOCAL VERIFY FAILED'};return{status:'PASS',summary:`API + REPLAY PASS • ${data.rows.length} ROW${data.rows.length===1?'':'S'} • ${hash.slice(0,8)}…`}}catch(err){const server=Number.isFinite(err?.status),reason=String(err?.code||err?.message||'UNREACHABLE').toUpperCase().slice(0,80);return{status:server?'FAIL':'WARN',summary:`${server?'API ERROR':'NETWORK UNAVAILABLE'} • ${reason}`}}}
function waitForDiagnosticWorker(worker,timeoutMs=1200){return new Promise(resolve=>{if(!worker||worker.state!=='installing'){resolve();return}let done=false,timer=null;const finish=()=>{if(done)return;done=true;if(timer!==null)clearTimeout(timer);worker.removeEventListener?.('statechange',inspect);resolve()},inspect=()=>{if(worker.state!=='installing')finish()};worker.addEventListener?.('statechange',inspect);timer=setTimeout(finish,timeoutMs);inspect()})}
function diagnosticWorkerStatus(worker,timeoutMs=900){return new Promise(resolve=>{if(!worker||typeof MessageChannel==='undefined'){resolve(null);return}const channel=new MessageChannel();let done=false,timer=null;const finish=value=>{if(done)return;done=true;if(timer!==null)clearTimeout(timer);try{channel.port1.close()}catch{}resolve(value)};channel.port1.onmessage=event=>finish(event.data||null);timer=setTimeout(()=>finish(null),timeoutMs);try{worker.postMessage({type:'DIAGNOSTIC_STATUS'},[channel.port2])}catch{finish(null)}})}
async function diagnosticServiceWorkerProbe(){if(!('serviceWorker'in navigator))return{status:'WARN',summary:'SERVICE WORKER UNSUPPORTED'};if(!/^https?:$/.test(location.protocol))return{status:'WARN',summary:'SERVICE WORKER INACTIVE ON THIS PROTOCOL'};let reg=swRegistration;try{if(!reg)reg=await navigator.serviceWorker.getRegistration('./')}catch(err){return{status:'WARN',summary:`REGISTRATION LOOKUP FAILED • ${String(err?.message||err).toUpperCase().slice(0,60)}`}}if(!reg)return{status:'WARN',summary:'NO SERVICE WORKER REGISTRATION'};let updateOk=true;try{await reg.update()}catch{updateOk=false}await waitForDiagnosticWorker(reg.installing);const waiting=!!reg.waiting,ready=syncWaitingUpdate(reg);if(ready!==waiting)return{status:'FAIL',summary:'WAITING / UPDATE-READY STATE MISMATCH'};const worker=reg.waiting||reg.active||reg.installing||navigator.serviceWorker.controller;if(!worker)return{status:'WARN',summary:`UPDATE CHECK ${updateOk?'PASS':'UNAVAILABLE'} • NO INSTALLED WORKER`};const status=await diagnosticWorkerStatus(worker);if(!status||status.type!=='VOIDCUT_SW_STATUS')return{status:'WARN',summary:`UPDATE CHECK ${updateOk?'PASS':'UNAVAILABLE'} • STATUS CHANNEL UNAVAILABLE`};let scriptBuild='';try{scriptBuild=new URL(worker.scriptURL).searchParams.get('build')||''}catch{}const expectedCache=`voidcut-shell-${status.build}`;if(status.build!==BUILD_ID||status.cache!==expectedCache||scriptBuild!==status.build)return{status:'FAIL',summary:`WORKER BUILD/CACHE MISMATCH • PAGE ${BUILD_ID} • WORKER ${status.build||'UNKNOWN'}`};return{status:updateOk?'PASS':'WARN',summary:`UPDATE CHECK ${updateOk?'PASS':'UNAVAILABLE'} • ${waiting?'WAITING / MANUAL APPLY':String(worker.state||'READY').toUpperCase()} • BUILD ${status.build}`}}
'''
html = replace_once(html, 'function bytesLabel(n){', helpers + 'function bytesLabel(n){', 'insert F20 diagnostic probes')

old_start = "async function runSystemChecks(){const el=ui.diagnosticsText;el.className='diag-box';el.textContent='RUNNING DETERMINISTIC SELF-CHECK…';await new Promise(r=>setTimeout(r,0));const failures=simDiagnosticFailures(),warnings=[],"
new_start = "async function runSystemChecks(){const el=ui.diagnosticsText;el.className='diag-box';el.textContent='RUNNING LIVE + DETERMINISTIC SELF-CHECK…';await new Promise(r=>setTimeout(r,0));const timingProbe=diagnosticRankedTimingProbe(),[leaderboardProbe,swProbe]=await Promise.all([diagnosticLeaderboardProbe(),diagnosticServiceWorkerProbe()]),failures=simDiagnosticFailures(),warnings=[],"
html = replace_once(html, old_start, new_start, 'runSystemChecks live probe start')

probe_aggregation_anchor = "if(!compat.storage)warnings.push('Persistent browser storage is unavailable; saves may be memory-only.');"
probe_aggregation = probe_aggregation_anchor + "for(const [label,probe] of [['LIVE LEADERBOARD',leaderboardProbe],['RANKED TIMING',timingProbe],['PWA UPDATE',swProbe]]){if(probe.status==='FAIL')failures.push(`${label}: ${probe.summary}.`);else if(probe.status==='WARN')warnings.push(`${label}: ${probe.summary}.`)}"
html = replace_once(html, probe_aggregation_anchor, probe_aggregation, 'diagnostic probe aggregation')

old_lines = "`ERROR GUARD: ${runtimeIssues.length?runtimeIssues.length+' CAPTURED':'CLEAN'}`,`PWA: ${sw} • ${display} • secure ${window.isSecureContext?'YES':'NO'} • fullscreen ${fullscreenActive()?'ACTIVE':fullscreenSupported()?'AVAILABLE':'UNSUPPORTED'}`"
new_lines = "`ERROR GUARD: ${runtimeIssues.length?runtimeIssues.length+' CAPTURED':'CLEAN'}`,`LIVE LEADERBOARD: ${leaderboardProbe.status} • ${leaderboardProbe.summary}`,`RANKED TIMING: ${timingProbe.status} • ${timingProbe.summary}`,`PWA UPDATE: ${swProbe.status} • ${swProbe.summary}`,`PWA: ${sw} • ${display} • secure ${window.isSecureContext?'YES':'NO'} • fullscreen ${fullscreenActive()?'ACTIVE':fullscreenSupported()?'AVAILABLE':'UNSUPPORTED'}`"
html = replace_once(html, old_lines, new_lines, 'diagnostic report live probe lines')

html = replace_once(
    html,
    '<div class="vd6-action-label"><span>01 / VERIFY</span><small>Checks the installed release and deterministic runtime.</small></div>',
    '<div class="vd6-action-label"><span>01 / VERIFY</span><small>Checks the installed release, live services, timing guards and PWA update state.</small></div>',
    'diagnostic action description',
)

index_path.write_text(html, encoding='utf-8')

sw = sw_path.read_text(encoding='utf-8')
old_message = """self.addEventListener('message', event => {\n  const type = event.data && event.data.type;\n  if (type === 'SKIP_WAITING') {\n    self.skipWaiting();\n  }\n});"""
new_message = """self.addEventListener('message', event => {\n  const type = event.data && event.data.type;\n  if (type === 'DIAGNOSTIC_STATUS') {\n    const port = event.ports && event.ports[0];\n    if (port) port.postMessage({ type: 'VOIDCUT_SW_STATUS', build: VOIDCUT_BUILD, cache: VOIDCUT_CACHE, scope: VOIDCUT_SCOPE });\n    return;\n  }\n  if (type === 'SKIP_WAITING') {\n    self.skipWaiting();\n  }\n});"""
sw = replace_once(sw, old_message, new_message, 'service-worker diagnostic status channel')
sw_path.write_text(sw, encoding='utf-8')

# F3's executable behavior checks already prove notify defaults remain true.
# Update only its source-string invariants to follow the new explicit notify
# forwarding used by F20 diagnostics.
f3 = f3_test_path.read_text(encoding='utf-8')
for old, new, label in [
    ("  \"invalidateRankedTiming('FRAME STALL')\",", "  \"invalidateRankedTiming('FRAME STALL',notify)\",", 'F3 frame-stall source invariant'),
    ("  \"invalidateRankedTiming('TIMING DRIFT')\",", "  \"invalidateRankedTiming('TIMING DRIFT',notify)\",", 'F3 timing-drift source invariant'),
    ("  \"invalidateRankedTiming('CATCH-UP LIMIT')\",", "  \"invalidateRankedTiming('CATCH-UP LIMIT',notify)\",", 'F3 catch-up source invariant'),
]:
    f3 = replace_once(f3, old, new, label)
f3_test_path.write_text(f3, encoding='utf-8')

reg = register_path.read_text(encoding='utf-8')
row = '| VC-024 | MEDIUM | Built-in diagnostics do not exercise live leaderboard API/replay retrieval, ranked timing integrity, or full SW update behavior. | F20 | OPEN |'
reg = replace_once(reg, row, row.replace('OPEN', 'FIXED — VERIFYING'), 'VC-024 register row')
reg += '''\n## F20 implementation record — live competition, ranked timing and PWA diagnostics\n\n- `VERIFY INSTALL` now performs three explicit probes in addition to the existing local deterministic checks. Probe outcomes are surfaced as `PASS`, `WARN`, or `FAIL` in the report and feed the overall diagnostic result.\n- The live leaderboard probe is read-only: it requests `/leaderboard?limit=5`, validates the server ruleset and row contract, then retrieves one published replay when available and requires both local replay validation and deterministic competitive verification. It never creates a profile, requests/consumes a run ticket, or submits a score. Network unavailability is a warning so offline/local play remains a supported diagnostic state; malformed or erroneous live API responses are failures.\n- The ranked timing probe exercises the actual frame-stall, cumulative timing-drift, catch-up-limit and timing-reset guards against synthetic ranked state. The probe snapshots and restores every touched global and passes `notify=false` through timing guard helpers, so diagnostics cannot consume a real ticket, alter run eligibility, or display synthetic gameplay warnings. Normal runtime calls omit that optional parameter and retain `notify=true`.\n- The service-worker probe performs a real `registration.update()` check, waits briefly for an installing worker to settle, synchronizes the existing waiting-worker UI state, and queries the waiting/active worker over a read-only `DIAGNOSTIC_STATUS` MessageChannel. The worker reports its build, cache namespace and scope; diagnostics require page build, worker build, worker script query and build-derived cache namespace to agree. Diagnostics never send `SKIP_WAITING`, so F15 manual activation semantics remain intact.\n- The diagnostics UI copy now states that VERIFY INSTALL includes live services, timing guards and PWA update state. No gameplay balance, scoring, save schema, replay rules, leaderboard mutation contract, cosmetic behavior or PWA activation policy changed.\n'''
register_path.write_text(reg, encoding='utf-8')
