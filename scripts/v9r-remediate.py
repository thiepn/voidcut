from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


def regex_once(text, pattern, replacement, label, flags=0):
    new, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one regex match, found {count}')
    return new


# ---------------------------------------------------------------------------
# Frontend release remediation
# ---------------------------------------------------------------------------
index_path = ROOT / 'index.html'
s = index_path.read_text(encoding='utf-8')

# Patch release identity without changing save/replay/deterministic rules.
s = s.replace('6.1.0', '6.1.1')
s = s.replace('version 6.0.0 stable release', 'version 6.1.1 stable release')

# Gameplay HUD truth: actual field removal and a non-misleading streak label.
s = replace_once(
    s,
    "ctx.fillText(`CH ${String(sim.chamber).padStart(2,'0')} / FIELD ${Math.round(sim.progress()*100)}%`,680,32)",
    "ctx.fillText(`CH ${String(sim.chamber).padStart(2,'0')} / FIELD ${Math.min(100,Math.round(sim.removed/sim.area*100))}%`,680,32)",
    'field wordmark semantics',
)
s = replace_once(
    s,
    "const tag=`×${hudMultiplier.toFixed(1)} / ${hudCombo} COMBO`",
    "const tag=`×${hudMultiplier.toFixed(1)} / ${hudCombo} CUT STREAK`",
    'combo label',
)

# Mastery: top rank no longer requires rare-modifier RNG.
s = replace_once(
    s,
    "{points:275,title:'VOIDMASTER',reward:'VOIDMASTER title'}",
    "{points:265,title:'VOIDMASTER',reward:'VOIDMASTER title'}",
    'VOIDMASTER threshold',
)

# Records: keep the historical runtime statistic but remove it from the headline tier.
s = replace_once(
    s,
    '<div class="record-card featured"><div class="record-label">LONGEST RUN</div><div id="recordLongest" class="record-value">—</div></div>',
    '<div class="record-card featured"><div class="record-label">LARGEST CUT</div><div id="recordLongest" class="record-value">—</div></div>',
    'headline longest-run card',
)
s = replace_once(
    s,
    "$('menuRecordLongest').textContent=(r.longestRunSeconds||0)>0?fmt(Math.round(r.longestRunSeconds)):'—';\n$('menuRecordLongestMeta').textContent=(r.longestRunSeconds||0)>0?'Survival':'No long run yet';",
    "$('menuRecordLongest').textContent=r.largestCut?`${r.largestCut.toFixed(1)}%`:'—';\n$('menuRecordLongestMeta').textContent=r.largestCut?'Largest cut':'No scored cut yet';",
    'menu longest-run preview',
)
s = replace_once(
    s,
    "$('recordLongest').textContent=(r.longestRunSeconds||0)>0?fmt(Math.round(r.longestRunSeconds)):'—';",
    "$('recordLongest').textContent=r.largestCut?`${r.largestCut.toFixed(1)}%`:'—';",
    'records headline longest-run value',
)

# Tutorial: teach the game, not the complete scoring formula.
s = regex_once(
    s,
    r"function showTutorialScoring\(\)\{tutorialLocked=true;ui\.tutorial\.innerHTML=`<span class=\\\"tutorial-kicker\\\">LESSON 3 / 3 • CLEAR & SCORE</span><strong>Remove at least 75% of the arena to clear a normal chamber\.</strong><br>Removed area earns points\. Bigger cuts and close calls multiply them; clearing adds chamber and efficiency bonuses\. D–S\+ chamber grades add increasingly large bonuses that scale with chamber depth\. Dividers are setup tools and score 0\.<br><button id=\\\"tutorialContinue\\\" class=\\\"primary\\\" style=\\\"width:100%;margin-top:12px\\\">START RUN</button>`;const btn=\$\('tutorialContinue'\);if\(btn\)btn\.addEventListener\('click',\(\)=>\{if\(tutorialMode&&tutorialStage===3\)completeInteractiveTutorial\(\)\},\{once:true\}\);announce\('[^']*'\)\}",
    "function showTutorialScoring(){tutorialLocked=true;ui.tutorial.innerHTML=`<span class=\"tutorial-kicker\">LESSON 3 / 3 • CLEAR & SCORE</span><strong>Clear at least 75% of a normal field.</strong><br>Bigger cuts score more. Riskier close calls can multiply the score. Dividers create safe setups but score no points.<br><button id=\"tutorialContinue\" class=\"primary\" style=\"width:100%;margin-top:12px\">START RUN</button>`;const btn=$('tutorialContinue');if(btn)btn.addEventListener('click',()=>{if(tutorialMode&&tutorialStage===3)completeInteractiveTutorial()},{once:true});announce('Lesson 3 of 3. Clear at least 75 percent of a normal field. Bigger cuts score more. Riskier close calls can multiply the score. Dividers create safe setups but score no points.')}",
    'tutorial scoring simplification',
)

# Reduced Motion: manual preference OR operating-system preference controls canvas decoration.
s = replace_once(
    s,
    'function motionReduced(){return !!save.settings.reducedMotion}',
    'function motionReduced(){return !!save.settings.reducedMotion||!!systemReducedMotion()}',
    'reduced-motion bridge',
)
s = s.replace('shake=save.settings.reducedMotion?0:', 'shake=motionReduced()?0:')
s = s.replace('if(gameplayVisible&&!save.settings.reducedMotion&&flash>.01)', 'if(gameplayVisible&&!motionReduced()&&flash>.01)')
s = s.replace('function worldMotion(now,scale=1){return save.settings.reducedMotion?0:', 'function worldMotion(now,scale=1){return motionReduced()?0:')
s = s.replace('if(now<visualHoldUntil&&!save.settings.reducedMotion)render=false', 'if(now<visualHoldUntil&&!motionReduced())render=false')

# Ranked/local visibility in the existing compact gameplay status strip.
old_update_challenge = "function updateChallengeHud(){ui.challengeHud.classList.add('hidden');vd2CompetitiveStatus={kind:'',text:'',tone:'neutral'};if(state!=='play'||!activeChallenge||!challengeAnalysis)return;const target=competitivePaceAt(challengeAnalysis,sim.runElapsed),delta=sim.score-target.score,sign=delta>0?'+':'';vd2CompetitiveStatus={kind:'duel',text:`DUEL ${sign}${delta.toLocaleString()} / YOU ${sim.score.toLocaleString()} / PACE ${target.score.toLocaleString()} / CH ${sim.chamber}:${target.chamber}`,tone:delta>=0?'accent':'danger'}}"
new_update_challenge = "function updateChallengeHud(){ui.challengeHud.classList.add('hidden');vd2CompetitiveStatus={kind:'',text:'',tone:'neutral'};if(state!=='play')return;if(activeChallenge&&challengeAnalysis){const target=competitivePaceAt(challengeAnalysis,sim.runElapsed),delta=sim.score-target.score,sign=delta>0?'+':'';vd2CompetitiveStatus={kind:'duel',text:`DUEL ${sign}${delta.toLocaleString()} / YOU ${sim.score.toLocaleString()} / PACE ${target.score.toLocaleString()} / CH ${sim.chamber}:${target.chamber}`,tone:delta>=0?'accent':'danger'};return}if(activeRunMode==='standard')vd2CompetitiveStatus=activeLeaderboardTicket?{kind:'ranked',text:'RANKED RUN • SERVER-SEEDED • VERIFIED ON COMPLETION',tone:'accent'}:{kind:'local',text:'LOCAL RUN • NOT LEADERBOARD-ELIGIBLE',tone:'neutral'}}"
s = replace_once(s, old_update_challenge, new_update_challenge, 'ranked/local status')

# Leaderboard persistence and identity safety.
old_lb_preamble = "const LEADERBOARD_API='https://voidcut-leaderboard.thiepn.workers.dev';\nconst LEADERBOARD_IDENTITY_KEY='voidcut.leaderboard.identity.v1';\nlet leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,pendingLeaderboardSubmission=null;\nfunction loadLeaderboardIdentity(){try{const x=JSON.parse(localStorage.getItem(LEADERBOARD_IDENTITY_KEY)||'null');return x&&typeof x.playerId==='string'&&typeof x.token==='string'&&typeof x.name==='string'?x:null}catch{return null}}\nfunction storeLeaderboardIdentity(x){try{localStorage.setItem(LEADERBOARD_IDENTITY_KEY,JSON.stringify(x));return true}catch{return false}}\nfunction clearLeaderboardIdentity(){try{localStorage.removeItem(LEADERBOARD_IDENTITY_KEY)}catch{}}"
new_lb_preamble = "const LEADERBOARD_API='https://voidcut-leaderboard.thiepn.workers.dev';\nconst LEADERBOARD_IDENTITY_KEY='voidcut.leaderboard.identity.v1',LEADERBOARD_PENDING_KEY='voidcut.leaderboard.pending.v1';\nlet leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,pendingLeaderboardSubmission=null;\nfunction loadLeaderboardIdentity(){try{const x=JSON.parse(localStorage.getItem(LEADERBOARD_IDENTITY_KEY)||'null');return x&&typeof x.playerId==='string'&&typeof x.token==='string'&&typeof x.name==='string'?x:null}catch{return null}}\nfunction storeLeaderboardIdentity(x){try{localStorage.setItem(LEADERBOARD_IDENTITY_KEY,JSON.stringify(x));return localStorage.getItem(LEADERBOARD_IDENTITY_KEY)!=null}catch{return false}}\nfunction clearLeaderboardIdentity(){try{localStorage.removeItem(LEADERBOARD_IDENTITY_KEY)}catch{}}\nfunction leaderboardStorageWritable(){const k='voidcut.leaderboard.storage-test';try{localStorage.setItem(k,'1');const ok=localStorage.getItem(k)==='1';localStorage.removeItem(k);return ok}catch{return false}}\nfunction loadLeaderboardPending(){try{const x=JSON.parse(localStorage.getItem(LEADERBOARD_PENDING_KEY)||'null');if(x?.replay&&x?.ticket?.ticketId&&Number(x.ticket.expiresAt)>Date.now())return x;if(x)localStorage.removeItem(LEADERBOARD_PENDING_KEY)}catch{}return null}\nfunction setLeaderboardPending(x){pendingLeaderboardSubmission=x||null;try{if(x)localStorage.setItem(LEADERBOARD_PENDING_KEY,JSON.stringify(x));else localStorage.removeItem(LEADERBOARD_PENDING_KEY)}catch{}return pendingLeaderboardSubmission}\nfunction clearLeaderboardPending(){return setLeaderboardPending(null)}\npendingLeaderboardSubmission=loadLeaderboardPending();"
s = replace_once(s, old_lb_preamble, new_lb_preamble, 'leaderboard persistence preamble')

s = replace_once(
    s,
    "function showLeaderboardJoin(message='Name this profile once to publish your verified score.'){const card=leaderboardJoinCard();card.classList.remove('hidden');$('leaderboardJoinStatus').textContent=message;setTimeout(()=>$('leaderboardNameInput')?.focus({preventScroll:true}),50)}",
    "function showLeaderboardJoin(message='Name this profile once to publish your verified score.'){const card=leaderboardJoinCard();card.classList.remove('hidden');$('leaderboardJoinStatus').textContent=message}",
    'leaderboard autofocus removal',
)

s = regex_once(
    s,
    r"async function createLeaderboardProfileFromCard\(\)\{[\s\S]*?\}\nasync function submitLeaderboardRun",
    "async function createLeaderboardProfileFromCard(){const input=$('leaderboardNameInput'),button=$('leaderboardJoinButton'),status=$('leaderboardJoinStatus'),name=(input?.value||'').trim().replace(/\\s+/g,' ');if(!/^[A-Za-z0-9 _-]{3,16}$/.test(name)){status.textContent='Use 3–16 letters, numbers, spaces, _ or -.';return}if(!leaderboardStorageWritable()){status.textContent='GLOBAL PROFILE CAN’T BE SAVED IN THIS BROWSER';return}button.disabled=true;status.textContent='CREATING PROFILE…';try{const data=await leaderboardRequest('/profile/create',{method:'POST',body:JSON.stringify({name})},false);if(!data?.player?.id||!data?.token)throw new Error('Invalid profile response');if(!storeLeaderboardIdentity({playerId:data.player.id,name:data.player.name,token:data.token}))throw new Error('Leaderboard identity could not be saved');status.textContent='PROFILE READY • VERIFYING RUN…';if(pendingLeaderboardSubmission)await submitLeaderboardRun(pendingLeaderboardSubmission.replay,pendingLeaderboardSubmission.ticket)}catch(err){status.textContent=err?.code==='name-taken'?'NAME ALREADY TAKEN':String(err?.message||'PROFILE CREATION FAILED').toUpperCase()}finally{button.disabled=false}}\nasync function submitLeaderboardRun",
    'leaderboard profile storage preflight',
    flags=re.M,
)

s = regex_once(
    s,
    r"async function submitLeaderboardRun\(replay,ticket\)\{[\s\S]*?\}\nfunction queueLeaderboardSubmission",
    "async function submitLeaderboardRun(replay,ticket){if(!replay||!ticket)return;setLeaderboardPending({replay,ticket});const ident=loadLeaderboardIdentity();if(!ident){showLeaderboardJoin();return}try{appendLeaderboardResult('GLOBAL VERIFYING');const data=await leaderboardRequest(`/run/submit/${encodeURIComponent(ticket.ticketId)}`,{method:'POST',body:JSON.stringify(replay)},true);clearLeaderboardPending();hideLeaderboardJoin();const rank=data?.rank?`GLOBAL #${Number(data.rank).toLocaleString()}`:'GLOBAL VERIFIED';ui.newBest.textContent=(ui.newBest.textContent||'').replace(/(?: • )?GLOBAL VERIFYING/g,'');appendLeaderboardResult(data?.personalBest?`${rank} • PERSONAL BEST`:rank)}catch(err){ui.newBest.textContent=(ui.newBest.textContent||'').replace(/(?: • )?GLOBAL VERIFYING/g,'');if(err?.status===401){clearLeaderboardIdentity();showLeaderboardJoin('Your local leaderboard identity expired. Choose a name to create a new one and submit this run.')}else if([400,403,409,410,413].includes(err?.status)){clearLeaderboardPending();appendLeaderboardResult('GLOBAL RUN REJECTED')}else appendLeaderboardResult('GLOBAL SUBMISSION SAVED • RETRYING WHEN ONLINE')}}\nfunction queueLeaderboardSubmission",
    'durable leaderboard submission',
    flags=re.M,
)

s = replace_once(
    s,
    "function queueLeaderboardSubmission(replay,ticket){if(!replay||!ticket)return;pendingLeaderboardSubmission={replay,ticket};if(loadLeaderboardIdentity())void submitLeaderboardRun(replay,ticket);else showLeaderboardJoin()}",
    "function queueLeaderboardSubmission(replay,ticket){if(!replay||!ticket)return;setLeaderboardPending({replay,ticket});if(loadLeaderboardIdentity())void submitLeaderboardRun(replay,ticket);else showLeaderboardJoin()}\nfunction retryPendingLeaderboardSubmission(){const pending=pendingLeaderboardSubmission||loadLeaderboardPending();if(!pending)return;if(Number(pending.ticket?.expiresAt)<=Date.now()){clearLeaderboardPending();return}pendingLeaderboardSubmission=pending;if(loadLeaderboardIdentity())void submitLeaderboardRun(pending.replay,pending.ticket)}\nwindow.addEventListener('online',retryPendingLeaderboardSubmission);",
    'leaderboard queue and retry',
)

# More explicit leaderboard affordance.
s = s.replace("$('competitionNote').textContent='SERVER-VERIFIED MAIN RUNS • REPLAY v9'", "$('competitionNote').textContent='SELECT A RUN TO WATCH • SERVER-VERIFIED • REPLAY v9'")

# User-facing diagnostics demotion and current contract labels.
s = s.replace('HELP & SYSTEM', 'HELP & DATA')
s = s.replace('SYSTEM CHECKS</button>', 'ADVANCED DIAGNOSTICS</button>')
s = s.replace('<div class="screen-kicker">05 / RELEASE INSTRUMENT</div><div class="pause-title">SYSTEM CHECKS</div><div class="screen-subtitle">Installation integrity, storage health and deterministic verification.</div>', '<div class="screen-kicker">ADVANCED / DIAGNOSTICS</div><div class="pause-title">DIAGNOSTICS</div><div class="screen-subtitle">Technical details for troubleshooting VOIDCUT.</div>')
s = s.replace('<span><small>BUILD</small><b>6.0.0</b></span><span><small>SAVE</small><b>16</b></span><span><small>REPLAY</small><b>8</b></span>', '<span><small>BUILD</small><b>6.1.1</b></span><span><small>SAVE</small><b>17</b></span><span><small>REPLAY</small><b>9</b></span>')
s = s.replace("'SAVE NOT PERSISTED • OPEN SYSTEM CHECKS'", "'PROGRESS CAN’T BE SAVED • OPEN SETTINGS'")
s = s.replace("'SESSION ISSUE CAPTURED • OPEN SYSTEM CHECKS'", "'SESSION ISSUE DETECTED • OPEN SETTINGS'")
s = s.replace("'SAVE RECOVERED FROM SNAPSHOT • SYSTEM CHECKS AVAILABLE'", "'PREVIOUS SAVE RECOVERED'")

# Critical health notices must survive compact/landscape rules.
health_css = "\n/* V9-R: critical save-health warnings are never hidden by compact layouts. */\n#menu.has-health-warning .health-note{display:block!important;visibility:visible!important;opacity:1!important;min-height:18px!important;max-width:min(560px,92vw)!important;padding:4px 8px!important;text-align:center!important;}\n"
s = replace_once(s, '</style>\n\n<link rel="stylesheet" href="./design/voidcut-design-system.css" />', health_css + '</style>\n\n<link rel="stylesheet" href="./design/voidcut-design-system.css" />', 'health warning CSS')

# Retry a durable ranked submission after startup without interrupting the player.
s = replace_once(
    s,
    "vd6InitUtilityLayer();renderCosmetics();showMenu();refreshInstall();refreshFullscreen();requestAnimationFrame(update);",
    "vd6InitUtilityLayer();renderCosmetics();showMenu();refreshInstall();refreshFullscreen();setTimeout(retryPendingLeaderboardSubmission,250);requestAnimationFrame(update);",
    'pending leaderboard startup retry',
)

index_path.write_text(s, encoding='utf-8')

# ---------------------------------------------------------------------------
# Service worker: preserve player-controlled UPDATE READY semantics.
# ---------------------------------------------------------------------------
sw_path = ROOT / 'sw.js'
sw = sw_path.read_text(encoding='utf-8')
sw = sw.replace("const VOIDCUT_CACHE_VERSION = '6.1.0-pwa4';", "const VOIDCUT_CACHE_VERSION = '6.1.1-pwa1';")
install_pattern = r"(self\.addEventListener\('install', event => \{\n  event\.waitUntil\(\(async \(\) => \{\n    const cache = await caches\.open\(VOIDCUT_CACHE\);\n    await cache\.addAll\(VOIDCUT_CORE_URLS\);)\n    await self\.skipWaiting\(\);(\n  \}\)\(\)\);\n\}\);)"
sw, n = re.subn(install_pattern, r"\1\2", sw, count=1)
if n != 1:
    raise SystemExit(f'service-worker install skipWaiting removal: expected one match, found {n}')
sw_path.write_text(sw, encoding='utf-8')

# ---------------------------------------------------------------------------
# Leaderboard Worker correctness.
# ---------------------------------------------------------------------------
worker_path = ROOT / 'leaderboard/src/index.js'
w = worker_path.read_text(encoding='utf-8')
w = w.replace("const RULESET = Object.freeze({ build: '6.1.0', replay: 9, arena: 2, director: 6 });", "const RULESET = Object.freeze({ build: '6.1.1', replay: 9, arena: 2, director: 6 });")
w = replace_once(w, "if (!/^[A-F0-9]{64}$/.test(hash))", "if (!/^[a-f0-9]{64}$/i.test(hash))", 'leaderboard replay hash validation')
worker_path.write_text(w, encoding='utf-8')

# Deploy workflow follows the patched frontend contract.
deploy_path = ROOT / '.github/workflows/deploy-voidcut-leaderboard.yml'
d = deploy_path.read_text(encoding='utf-8')
d = d.replace('Check v6.1 frontend contract', 'Check v6.1.1 frontend contract')
d = d.replace('voidcut-build\" content=\"6.1.0', 'voidcut-build\" content=\"6.1.1')
d = d.replace('until the v6.1 frontend patch lands.', 'until the v6.1.1 frontend patch lands.')
deploy_path.write_text(d, encoding='utf-8')

print('V9-R remediation applied: build 6.1.1, deterministic rules unchanged.')
