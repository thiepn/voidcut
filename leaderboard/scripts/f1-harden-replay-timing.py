from pathlib import Path

root = Path(__file__).resolve().parents[2]
index_path = root / 'index.html'
register_path = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'

text = index_path.read_text(encoding='utf-8')
original = text


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    text = text.replace(old, new, 1)


replace_once(
    "const REPLAY_EVENT_LIMIT=50000,REPLAY_CODE_LIMIT=12000000;",
    "const REPLAY_EVENT_LIMIT=50000,REPLAY_CODE_LIMIT=12000000,REPLAY_TIME_EPS=1e-6;\nfunction replayInputTiming(r,e,simTime){if(r?.version<9)return e.t<=simTime+REPLAY_TIME_EPS?'due':'future';if(e.t<simTime-REPLAY_TIME_EPS)return'stale';if(e.t<=simTime+REPLAY_TIME_EPS)return'due';return'future'}",
    'insert strict replay timing helper',
)

old_validation = "function replayValidationReason(r){if(!r||typeof r!=='object')return'not-object';const supported=r.version===1||(r.version===2&&(r.arenaGeneration||2)===2)||(r.version===3&&(r.arenaGeneration||2)===2&&(r.directorGeneration||2)===2)||(r.version===4&&(r.arenaGeneration||2)===2&&(r.directorGeneration||3)===3)||(r.version===5&&(r.arenaGeneration||2)===2&&(r.directorGeneration||4)===4)||(r.version===6&&(r.arenaGeneration||2)===2&&(r.directorGeneration||5)===5)||(r.version===7&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6)||(r.version===8&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6)||(r.version===9&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6);if(!supported)return'unsupported-ruleset';if(!Number.isInteger(r.seed)||r.seed<0||r.seed>0xffffffff)return'invalid-seed';if(!Number.isSafeInteger(r.score)||r.score<0||!Number.isSafeInteger(r.chamber)||r.chamber<1||!Number.isFinite(r.deathTime)||r.deathTime<0)return'invalid-result';if(!Array.isArray(r.events)||r.events.length>REPLAY_EVENT_LIMIT)return'invalid-events';let prev=-Infinity;for(const e of r.events){const dl=Math.hypot(e?.d?.x,e?.d?.y);if(!Number.isFinite(e?.t)||e.t<0||e.t+1e-8<prev||e.t>r.deathTime+.25||!Number.isFinite(e?.o?.x)||!Number.isFinite(e?.o?.y)||!Number.isFinite(e?.d?.x)||!Number.isFinite(e?.d?.y)||dl<.5||dl>1.5)return'invalid-events';prev=e.t}if(typeof r.hash!=='string'||r.hash!==replayHash(r))return'hash-mismatch';return'valid'}"
new_validation = "function replayValidationReason(r){if(!r||typeof r!=='object')return'not-object';const supported=r.version===1||(r.version===2&&(r.arenaGeneration||2)===2)||(r.version===3&&(r.arenaGeneration||2)===2&&(r.directorGeneration||2)===2)||(r.version===4&&(r.arenaGeneration||2)===2&&(r.directorGeneration||3)===3)||(r.version===5&&(r.arenaGeneration||2)===2&&(r.directorGeneration||4)===4)||(r.version===6&&(r.arenaGeneration||2)===2&&(r.directorGeneration||5)===5)||(r.version===7&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6)||(r.version===8&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6)||(r.version===9&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6);if(!supported)return'unsupported-ruleset';if(!Number.isInteger(r.seed)||r.seed<0||r.seed>0xffffffff)return'invalid-seed';if(!Number.isSafeInteger(r.score)||r.score<0||!Number.isSafeInteger(r.chamber)||r.chamber<1||!Number.isFinite(r.deathTime)||r.deathTime<0)return'invalid-result';if(!Array.isArray(r.events)||r.events.length>REPLAY_EVENT_LIMIT)return'invalid-events';let prev=-Infinity;for(const e of r.events){const dl=Math.hypot(e?.d?.x,e?.d?.y),badOrder=r.version>=9?e?.t<=prev+REPLAY_TIME_EPS:e?.t+1e-8<prev,maxEventTime=r.deathTime+(r.version>=9?REPLAY_TIME_EPS:.25);if(!Number.isFinite(e?.t)||e.t<0||badOrder||e.t>maxEventTime||!Number.isFinite(e?.o?.x)||!Number.isFinite(e?.o?.y)||!Number.isFinite(e?.d?.x)||!Number.isFinite(e?.d?.y)||dl<.5||dl>1.5)return'invalid-events';prev=e.t}if(typeof r.hash!=='string'||r.hash!==replayHash(r))return'hash-mismatch';return'valid'}"
replace_once(old_validation, new_validation, 'harden replay validation')

old_analyze = "function analyzeReplayData(data){if(!validReplay(data))return null;const s=new Sim(data.seed);s.reset(data.seed,replayArenaGeneration(data),replayDirectorGeneration(data),replayScoringVersion(data));let idx=0,active=null,died=false,deathCut=null;const cuts=[],limit=data.deathTime+DT*4;while(s.runElapsed<=limit&&!died){while(idx<data.events.length&&data.events[idx].t<=s.runElapsed+1e-6&&!s.cut){const e=data.events[idx],reg=s.regionAt(e.o);if(!reg||!s.beginCut(reg.id,e.o,e.d))break;active=idx;idx++}const r=s.update(DT);if(r.dead){died=true;if(active!=null){const e=data.events[active];cuts.push({i:active,start:e.t,end:s.runElapsed,ch:s.chamber,outcome:'death',pct:0,gain:0,clear:null,quality:'DEATH',threat:s.cut?.threatened?.size||0,complete:false,grade:null,scoreAfter:s.score,chamberAfter:s.chamber});deathCut=active}break}if(r.res&&active!=null){const x=r.res,e=data.events[active];cuts.push({i:active,start:e.t,end:s.runElapsed,ch:s.chamber,outcome:x.divider?'divider':'removed',pct:x.pct,gain:x.gain,clear:Number.isFinite(x.clearance)?x.clearance:null,quality:x.quality,threat:x.threatened,complete:x.complete,grade:x.grade,scoreAfter:s.score,chamberAfter:s.chamber+(x.complete?1:0)});active=null;if(x.complete)s.advance()}}const resolved=cuts.filter(x=>x.outcome!=='death'),big=resolved.reduce((a,b)=>!a||b.pct>a.pct?b:a,null),close=resolved.filter(x=>x.clear!=null).reduce((a,b)=>!a||b.clear<a.clear?b:a,null),verified=died&&s.score===data.score&&s.chamber===data.chamber&&Math.abs(s.runElapsed-data.deathTime)<=DT*2.1;return{cuts,big:big?.i??null,close:close?.i??null,death:deathCut,verified}}"
new_analyze = "function analyzeReplayData(data){if(!validReplay(data))return null;const s=new Sim(data.seed);s.reset(data.seed,replayArenaGeneration(data),replayDirectorGeneration(data),replayScoringVersion(data));let idx=0,active=null,died=false,deathCut=null,invalidReason=null;const cuts=[],limit=data.deathTime+DT*4;while(s.runElapsed<=limit&&!died&&!invalidReason){while(idx<data.events.length&&!s.cut){const e=data.events[idx],timing=replayInputTiming(data,e,s.runElapsed);if(timing==='future')break;if(timing==='stale'){invalidReason='stale-input';break}const reg=s.regionAt(e.o);if(!reg||!s.beginCut(reg.id,e.o,e.d)){invalidReason='invalid-input';break}active=idx;idx++}if(invalidReason)break;const r=s.update(DT);if(r.dead){died=true;if(active!=null){const e=data.events[active];cuts.push({i:active,start:e.t,end:s.runElapsed,ch:s.chamber,outcome:'death',pct:0,gain:0,clear:null,quality:'DEATH',threat:s.cut?.threatened?.size||0,complete:false,grade:null,scoreAfter:s.score,chamberAfter:s.chamber});deathCut=active}break}if(r.res&&active!=null){const x=r.res,e=data.events[active];cuts.push({i:active,start:e.t,end:s.runElapsed,ch:s.chamber,outcome:x.divider?'divider':'removed',pct:x.pct,gain:x.gain,clear:Number.isFinite(x.clearance)?x.clearance:null,quality:x.quality,threat:x.threatened,complete:x.complete,grade:x.grade,scoreAfter:s.score,chamberAfter:s.chamber+(x.complete?1:0)});active=null;if(x.complete)s.advance()}}const resolved=cuts.filter(x=>x.outcome!=='death'),big=resolved.reduce((a,b)=>!a||b.pct>a.pct?b:a,null),close=resolved.filter(x=>x.clear!=null).reduce((a,b)=>!a||b.clear<a.clear?b:a,null),verified=!invalidReason&&died&&idx===data.events.length&&s.score===data.score&&s.chamber===data.chamber&&Math.abs(s.runElapsed-data.deathTime)<=DT*2.1;return{cuts,big:big?.i??null,close:close?.i??null,death:deathCut,verified,invalidReason}}"
replace_once(old_analyze, new_analyze, 'harden replay analysis')

old_seek = "function seekReplay(time){if(state!=='replay'||!replayData)return;transitionSerial++;transition=false;transitionResult=null;const target=Math.max(0,Math.min(replayData.deathTime-DT*.5,+time||0)),s=new Sim(replayData.seed);s.reset(replayData.seed,replayArenaGeneration(replayData),replayDirectorGeneration(replayData),replayScoringVersion(replayData));let idx=0,active=null,died=false;while(s.runElapsed+DT<=target+1e-9&&!died){while(idx<replayData.events.length&&replayData.events[idx].t<=s.runElapsed+1e-6&&!s.cut){const e=replayData.events[idx],reg=s.regionAt(e.o);if(!reg||!s.beginCut(reg.id,e.o,e.d))break;active=idx;idx++}const r=s.update(DT);if(r.dead){died=true;break}if(r.res&&active!=null){active=null;if(r.res.complete)s.advance()}}sim=s;rebuildRenderGeometry();bounceState.clear();replayIndex=idx;replayPaused=true;acc=0;shownScore=sim.score;scorePulse=0;shake=0;hudMultiplier=1;hudCombo=0;dangerPulse=0;deathImpact=0;visualHoldUntil=0;clearFx();stopCutHum();$('replayPause').textContent='RESUME';updateReplayHud()}"
new_seek = "function seekReplay(time){if(state!=='replay'||!replayData)return;transitionSerial++;transition=false;transitionResult=null;const target=Math.max(0,Math.min(replayData.deathTime-DT*.5,+time||0)),s=new Sim(replayData.seed);s.reset(replayData.seed,replayArenaGeneration(replayData),replayDirectorGeneration(replayData),replayScoringVersion(replayData));let idx=0,active=null,died=false,invalid=false;while(s.runElapsed+DT<=target+1e-9&&!died&&!invalid){while(idx<replayData.events.length&&!s.cut){const e=replayData.events[idx],timing=replayInputTiming(replayData,e,s.runElapsed);if(timing==='future')break;if(timing==='stale'){invalid=true;break}const reg=s.regionAt(e.o);if(!reg||!s.beginCut(reg.id,e.o,e.d)){invalid=true;break}active=idx;idx++}if(invalid)break;const r=s.update(DT);if(r.dead){died=true;break}if(r.res&&active!=null){active=null;if(r.res.complete)s.advance()}}if(invalid){finishReplay('INPUT TIMING MISMATCH');return}sim=s;rebuildRenderGeometry();bounceState.clear();replayIndex=idx;replayPaused=true;acc=0;shownScore=sim.score;scorePulse=0;shake=0;hudMultiplier=1;hudCombo=0;dangerPulse=0;deathImpact=0;visualHoldUntil=0;clearFx();stopCutHum();$('replayPause').textContent='RESUME';updateReplayHud()}"
replace_once(old_seek, new_seek, 'harden replay seek')

old_playback = "while(replayIndex<replayData.events.length&&replayData.events[replayIndex].t<=sim.runElapsed+1e-6&&!sim.cut){const e=replayData.events[replayIndex++],reg=sim.regionAt(e.o);if(!reg||!sim.beginCut(reg.id,e.o,e.d)){finishReplay('INPUT DIVERGED');break}startCutHum()}"
new_playback = "while(replayIndex<replayData.events.length&&!sim.cut){const e=replayData.events[replayIndex],timing=replayInputTiming(replayData,e,sim.runElapsed);if(timing==='future')break;if(timing==='stale'){finishReplay('INPUT TIMING MISMATCH');break}replayIndex++;const reg=sim.regionAt(e.o);if(!reg||!sim.beginCut(reg.id,e.o,e.d)){finishReplay('INPUT DIVERGED');break}startCutHum()}"
replace_once(old_playback, new_playback, 'harden replay playback')

probe_anchor = "const scoreProbe={version:9,arenaGeneration:2,directorGeneration:6,seed:0x50100001,events:[{t:1,o:{x:200,y:300},d:{x:1,y:0}}],score:3000000000,chamber:1200,deathTime:2,hash:''};"
probe_insert = "const strictTimingProbe={version:9},legacyTimingProbe={version:8};if(replayInputTiming(strictTimingProbe,{t:1},1)!=='due'||replayInputTiming(strictTimingProbe,{t:1},1+DT)!=='stale'||replayInputTiming(strictTimingProbe,{t:1+DT},1)!=='future')failures.push('Strict replay input timing contract failed.');else notes.push('Strict replay input timing PASS');if(replayInputTiming(legacyTimingProbe,{t:1},1+DT)!=='due')failures.push('Legacy replay timing compatibility failed.');else notes.push('Legacy replay timing compatibility PASS');const duplicateTimingProbe={version:9,arenaGeneration:2,directorGeneration:6,seed:0x50100003,events:[{t:1,o:{x:200,y:300},d:{x:1,y:0}},{t:1,o:{x:210,y:300},d:{x:0,y:1}}],score:0,chamber:1,deathTime:2,hash:''};duplicateTimingProbe.hash=replayHash(duplicateTimingProbe);if(replayValidationReason(duplicateTimingProbe)!=='invalid-events')failures.push('Replay duplicate input timestamp was accepted.');else notes.push('Duplicate replay timestamp rejection PASS');\n" + probe_anchor
replace_once(probe_anchor, probe_insert, 'add replay timing regression diagnostics')

if text == original:
    raise SystemExit('index.html was not modified')
index_path.write_text(text, encoding='utf-8')

register = register_path.read_text(encoding='utf-8')
old_row = "| VC-001 | CRITICAL | Replay verifier treats timestamps as not-before times, allowing stale/queued cuts to execute later with zero input delay. | F1 | OPEN |"
new_row = "| VC-001 | CRITICAL | Replay verifier treats timestamps as not-before times, allowing stale/queued cuts to execute later with zero input delay. | F1 | FIXED — VERIFYING |"
if register.count(old_row) != 1:
    raise SystemExit('fix register VC-001 row was not found exactly once')
register = register.replace(old_row, new_row, 1)
register += """

## F1 implementation record — strict replay input timing

- Current replay v9 input timestamps are now treated as exact deterministic simulation-time input starts within `REPLAY_TIME_EPS = 1e-6`, not as `not-before` queue times.
- A v9 input that becomes older than the current simulation time is rejected as `stale-input`; it is never deferred until the active cut finishes.
- v9 event timestamps must be strictly increasing, so identical input-start timestamps are invalid before simulation.
- v9 events later than `deathTime + REPLAY_TIME_EPS` are invalid.
- Deterministic verification now requires every replay event to have been consumed when death occurs, preventing ignored post-death inputs from verifying.
- Replay playback and replay seeking use the same timing classifier as local/server analysis and fail closed on stale timing.
- Replay v1–v8 retain the legacy `not-before` timing behavior for local backward-compatible viewing.
- Built-in stress diagnostics now cover strict due/stale/future classification, legacy timing compatibility, and duplicate v9 timestamp rejection.
- The generated Cloudflare verifier must be rebuilt from this source before F1 is closed.

F1 changes are limited to replay timing integrity and regression coverage; gameplay balance, visuals, game modes and save schema remain unchanged.
"""
register_path.write_text(register, encoding='utf-8')

print('F1 replay timing hardening patch applied successfully.')
