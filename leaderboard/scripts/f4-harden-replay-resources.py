from pathlib import Path

root = Path(__file__).resolve().parents[2]
index = root / 'index.html'
worker = root / 'leaderboard' / 'src' / 'index.js'
builder = root / 'leaderboard' / 'scripts' / 'build-verifier.mjs'
register = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

# Browser/runtime source: preserve broad local replay compatibility, but add a
# separate competitive validation policy and an independent verifier step cap.
s = index.read_text(encoding='utf-8')
s = replace_once(
    s,
    "const REPLAY_EVENT_LIMIT=50000,REPLAY_CODE_LIMIT=12000000,REPLAY_TIME_EPS=1e-6;",
    "const REPLAY_EVENT_LIMIT=50000,REPLAY_CODE_LIMIT=12000000,REPLAY_TIME_EPS=1e-6;\nconst COMPETITIVE_REPLAY_EVENT_LIMIT=12000,COMPETITIVE_REPLAY_MAX_DURATION=1800,COMPETITIVE_REPLAY_MAX_STEPS=216100;",
    'competitive replay constants',
)
s = replace_once(
    s,
    "function validReplay(r){return replayValidationReason(r)==='valid'}",
    "function competitiveReplayValidationReason(r){const base=replayValidationReason(r);if(base!=='valid')return base;if(r?.version!==9)return'unsupported-ruleset';if(r.events.length>COMPETITIVE_REPLAY_EVENT_LIMIT||r.deathTime>COMPETITIVE_REPLAY_MAX_DURATION)return'resource-limit';return'valid'}\nfunction validReplay(r){return replayValidationReason(r)==='valid'}",
    'competitive replay validation',
)
old_analyzer = "function analyzeReplayData(data){if(!validReplay(data))return null;const s=new Sim(data.seed);s.reset(data.seed,replayArenaGeneration(data),replayDirectorGeneration(data),replayScoringVersion(data));let idx=0,active=null,died=false,deathCut=null,invalidReason=null;const cuts=[],limit=data.deathTime+DT*4;while(s.runElapsed<=limit&&!died&&!invalidReason){while(idx<data.events.length&&!s.cut){const e=data.events[idx],timing=replayInputTiming(data,e,s.runElapsed);if(timing==='future')break;if(timing==='stale'){invalidReason='stale-input';break}const reg=s.regionAt(e.o);if(!reg||!s.beginCut(reg.id,e.o,e.d)){invalidReason='invalid-input';break}active=idx;idx++}if(invalidReason)break;const r=s.update(DT);if(r.dead){died=true;if(active!=null){const e=data.events[active];cuts.push({i:active,start:e.t,end:s.runElapsed,ch:s.chamber,outcome:'death',pct:0,gain:0,clear:null,quality:'DEATH',threat:s.cut?.threatened?.size||0,complete:false,grade:null,scoreAfter:s.score,chamberAfter:s.chamber});deathCut=active}break}if(r.res&&active!=null){const x=r.res,e=data.events[active];cuts.push({i:active,start:e.t,end:s.runElapsed,ch:s.chamber,outcome:x.divider?'divider':'removed',pct:x.pct,gain:x.gain,clear:Number.isFinite(x.clearance)?x.clearance:null,quality:x.quality,threat:x.threatened,complete:x.complete,grade:x.grade,scoreAfter:s.score,chamberAfter:s.chamber+(x.complete?1:0)});active=null;if(x.complete)s.advance()}}const resolved=cuts.filter(x=>x.outcome!=='death'),big=resolved.reduce((a,b)=>!a||b.pct>a.pct?b:a,null),close=resolved.filter(x=>x.clear!=null).reduce((a,b)=>!a||b.clear<a.clear?b:a,null),verified=!invalidReason&&died&&idx===data.events.length&&s.score===data.score&&s.chamber===data.chamber&&Math.abs(s.runElapsed-data.deathTime)<=DT*2.1;return{cuts,big:big?.i??null,close:close?.i??null,death:deathCut,verified,invalidReason}}"
new_analyzer = "function analyzeReplayData(data,competitive=false){const validation=competitive?competitiveReplayValidationReason(data):replayValidationReason(data);if(validation!=='valid')return null;const s=new Sim(data.seed);s.reset(data.seed,replayArenaGeneration(data),replayDirectorGeneration(data),replayScoringVersion(data));let idx=0,active=null,died=false,deathCut=null,invalidReason=null,steps=0;const cuts=[],limit=data.deathTime+DT*4;while(s.runElapsed<=limit&&!died&&!invalidReason){if(competitive&&steps>=COMPETITIVE_REPLAY_MAX_STEPS){invalidReason='step-budget';break}steps++;while(idx<data.events.length&&!s.cut){const e=data.events[idx],timing=replayInputTiming(data,e,s.runElapsed);if(timing==='future')break;if(timing==='stale'){invalidReason='stale-input';break}const reg=s.regionAt(e.o);if(!reg||!s.beginCut(reg.id,e.o,e.d)){invalidReason='invalid-input';break}active=idx;idx++}if(invalidReason)break;const r=s.update(DT);if(r.dead){died=true;if(active!=null){const e=data.events[active];cuts.push({i:active,start:e.t,end:s.runElapsed,ch:s.chamber,outcome:'death',pct:0,gain:0,clear:null,quality:'DEATH',threat:s.cut?.threatened?.size||0,complete:false,grade:null,scoreAfter:s.score,chamberAfter:s.chamber});deathCut=active}break}if(r.res&&active!=null){const x=r.res,e=data.events[active];cuts.push({i:active,start:e.t,end:s.runElapsed,ch:s.chamber,outcome:x.divider?'divider':'removed',pct:x.pct,gain:x.gain,clear:Number.isFinite(x.clearance)?x.clearance:null,quality:x.quality,threat:x.threatened,complete:x.complete,grade:x.grade,scoreAfter:s.score,chamberAfter:s.chamber+(x.complete?1:0)});active=null;if(x.complete)s.advance()}}const resolved=cuts.filter(x=>x.outcome!=='death'),big=resolved.reduce((a,b)=>!a||b.pct>a.pct?b:a,null),close=resolved.filter(x=>x.clear!=null).reduce((a,b)=>!a||b.clear<a.clear?b:a,null),verified=!invalidReason&&died&&idx===data.events.length&&s.score===data.score&&s.chamber===data.chamber&&Math.abs(s.runElapsed-data.deathTime)<=DT*2.1;return{cuts,big:big?.i??null,close:close?.i??null,death:deathCut,verified,invalidReason,steps}}"
s = replace_once(s, old_analyzer, new_analyzer, 'bounded replay analyzer')
index.write_text(s, encoding='utf-8')

# Generated server verifier must opt into the competitive limits.
b = builder.read_text(encoding='utf-8')
b = replace_once(
    b,
    "  const analysis=analyzeReplayData(replay);",
    "  const analysis=analyzeReplayData(replay,true);",
    'generated verifier competitive mode',
)
builder.write_text(b, encoding='utf-8')

# Worker: reduce accepted replay bytes, preflight structural limits before the
# deterministic simulation, and stream-read with a byte counter so chunked
# bodies cannot force an unbounded request.text() allocation.
w = worker.read_text(encoding='utf-8')
w = replace_once(
    w,
    "const MAX_REPLAY_BYTES = 12_500_000;",
    "const MAX_REPLAY_BYTES = 2_500_000;\nconst MAX_COMPETITIVE_EVENTS = 12_000;\nconst MAX_COMPETITIVE_DURATION = 1_800;",
    'worker replay limits',
)
read_json = "async function readJson(request, maxBytes = 32_000) {\n  const len = Number(request.headers.get('Content-Length') || 0);\n  if (len && len > maxBytes) throw new Error('body-too-large');\n  const text = await request.text();\n  if (text.length > maxBytes) throw new Error('body-too-large');\n  return text ? JSON.parse(text) : {};\n}"
bounded = read_json + "\nasync function readBoundedText(request, maxBytes) {\n  const len = Number(request.headers.get('Content-Length') || 0);\n  if (len && len > maxBytes) throw new Error('body-too-large');\n  if (!request.body) return '';\n  const reader = request.body.getReader();\n  const decoder = new TextDecoder();\n  let total = 0;\n  let text = '';\n  try {\n    while (true) {\n      const { done, value } = await reader.read();\n      if (done) break;\n      total += value?.byteLength || 0;\n      if (total > maxBytes) throw new Error('body-too-large');\n      text += decoder.decode(value, { stream: true });\n    }\n    text += decoder.decode();\n    return text;\n  } catch (err) {\n    try { await reader.cancel(); } catch {}\n    throw err;\n  }\n}"
w = replace_once(w, read_json, bounded, 'bounded stream reader')
old_read = "    let text;\n    try {\n      const len = Number(request.headers.get('Content-Length') || 0);\n      if (len && len > MAX_REPLAY_BYTES) throw new Error('too-large');\n      text = await request.text();\n      if (text.length > MAX_REPLAY_BYTES) throw new Error('too-large');\n    } catch {\n      return error(request, 413, 'replay-too-large', 'Replay is too large.');\n    }"
new_read = "    let text;\n    try {\n      text = await readBoundedText(request, MAX_REPLAY_BYTES);\n    } catch {\n      return error(request, 413, 'replay-too-large', 'Replay is too large.');\n    }"
w = replace_once(w, old_read, new_read, 'bounded verifier request read')
seed_line = "    if ((replay.seed >>> 0) !== (Number(ticket.seed) >>> 0)) return this.#reject(request, ticketId, 'seed-mismatch', 'Replay seed does not match its server-issued run ticket.');\n\n    const official = verifyReplay(replay);"
preflight = "    if ((replay.seed >>> 0) !== (Number(ticket.seed) >>> 0)) return this.#reject(request, ticketId, 'seed-mismatch', 'Replay seed does not match its server-issued run ticket.');\n    if (!Array.isArray(replay.events) || replay.events.length > MAX_COMPETITIVE_EVENTS || !Number.isFinite(replay.deathTime) || replay.deathTime < 0 || replay.deathTime > MAX_COMPETITIVE_DURATION) {\n      return this.#reject(request, ticketId, 'replay-resource-limit', 'Replay exceeds competitive verification limits.');\n    }\n\n    const official = verifyReplay(replay);"
w = replace_once(w, seed_line, preflight, 'worker replay preflight')
worker.write_text(w, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old = '| VC-004 | HIGH | Replay verifier lacks a hard maximum simulation duration/step budget and can be forced into excessive CPU work. | F4 | OPEN |'
new = '| VC-004 | HIGH | Replay verifier lacks a hard maximum simulation duration/step budget and can be forced into excessive CPU work. | F4 | FIXED — VERIFYING |'
if r.count(old) != 1:
    raise SystemExit('VC-004 register marker missing')
r = r.replace(old, new, 1)
r += '''\n## F4 implementation record — replay verifier resource ceilings\n\n- Current competitive replay verification now has explicit pre-simulation ceilings: 30 minutes (`1800 s`), 12,000 input events, and 216,100 deterministic simulation steps.\n- The step counter is independent of replay `deathTime`, so verifier termination no longer depends solely on attacker-controlled duration fields or simulation-clock progress.\n- Browser/local replay compatibility keeps the existing broader 50,000-event / 12 MB import envelope; the tighter ceilings apply only when `analyzeReplayData(..., true)` is used by the generated global verifier.\n- The generated verifier now explicitly invokes competitive analyzer mode.\n- The leaderboard Worker rejects over-limit event counts/durations before deterministic verification and before replay hashing/storage.\n- Maximum leaderboard replay request size is reduced from 12.5 MB to 2.5 MB.\n- Durable Object replay ingestion now reads the request stream incrementally with a byte counter and cancels once the limit is crossed, including when `Content-Length` is missing or false.\n- Existing edge `Content-Length` rejection remains as an earlier fast path.\n\nF4 does not change physics, scoring, save schema, replay version, local replay playback rules, or gameplay balance.\n'''
register.write_text(r, encoding='utf-8')
