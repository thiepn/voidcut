from pathlib import Path

root = Path(__file__).resolve().parents[2]
index = root / 'index.html'
client = root / 'leaderboard' / 'client' / 'global-leaderboard-runtime.js'
register = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


helper_old = """async function prefetchLeaderboardTicket(){if(leaderboardTicket&&leaderboardTicket.expiresAt>Date.now()+60000)return leaderboardTicket;if(leaderboardTicketPromise)return leaderboardTicketPromise;leaderboardTicketPromise=(async()=>{try{const data=await leaderboardRequest('/run/start',{method:'POST',body:'{}'},true);if(data?.ticketId&&Number.isInteger(data.seed)&&data?.ruleset?.replay===9){leaderboardTicket={ticketId:data.ticketId,seed:data.seed>>>0,expiresAt:Number(data.expiresAt)||0};return leaderboardTicket}}catch{}return null})().finally(()=>{leaderboardTicketPromise=null});return leaderboardTicketPromise}
function takeLeaderboardTicket(){if(!leaderboardTicket||leaderboardTicket.expiresAt<=Date.now()+1000){leaderboardTicket=null;return null}const t=leaderboardTicket;leaderboardTicket=null;return t}
"""
helper_new = """async function prefetchLeaderboardTicket(){if(leaderboardTicket&&leaderboardTicket.expiresAt>Date.now()+60000)return leaderboardTicket;if(leaderboardTicketPromise)return leaderboardTicketPromise;leaderboardTicketPromise=(async()=>{try{const data=await leaderboardRequest('/run/start',{method:'POST',body:'{}'},true);if(data?.ticketId&&Number.isInteger(data.seed)&&data?.ruleset?.replay===9){leaderboardTicket={ticketId:data.ticketId,seed:data.seed>>>0,expiresAt:Number(data.expiresAt)||0};return leaderboardTicket}}catch{}return null})().finally(()=>{leaderboardTicketPromise=null});return leaderboardTicketPromise}
function takeLeaderboardTicket(){if(!leaderboardTicket||leaderboardTicket.expiresAt<=Date.now()+1000){leaderboardTicket=null;return null}const t=leaderboardTicket;leaderboardTicket=null;return t}
async function acquireLeaderboardTicket(waitMs=RANKED_START_WAIT_MS){const ready=takeLeaderboardTicket();if(ready)return{ticket:ready,reason:null};const request=prefetchLeaderboardTicket();let timer=null;const outcome=await Promise.race([request.then(()=>'settled'),new Promise(resolve=>{timer=setTimeout(()=>resolve('timeout'),Math.max(0,Number(waitMs)||0))})]);if(timer!==null)clearTimeout(timer);const ticket=takeLeaderboardTicket();if(ticket)return{ticket,reason:null};return{ticket:null,reason:outcome==='timeout'?'LEADERBOARD TIMEOUT':'LEADERBOARD UNAVAILABLE'}}
"""

# Keep the source client fragment aligned with the shipped inline runtime.
c = client.read_text(encoding='utf-8')
c = replace_once(
    c,
    "const LEADERBOARD_IDENTITY_KEY='voidcut.leaderboard.identity.v1';\n",
    "const LEADERBOARD_IDENTITY_KEY='voidcut.leaderboard.identity.v1';\nconst RANKED_START_WAIT_MS=2000;\n",
    'client ranked start constant',
)
c = replace_once(c, helper_old, helper_new, 'client ticket acquisition helper')
client.write_text(c, encoding='utf-8')

s = index.read_text(encoding='utf-8')
s = replace_once(
    s,
    "const LEADERBOARD_IDENTITY_KEY='voidcut.leaderboard.identity.v1';\n",
    "const LEADERBOARD_IDENTITY_KEY='voidcut.leaderboard.identity.v1';\nconst RANKED_START_WAIT_MS=2000;\n",
    'inline ranked start constant',
)
s = replace_once(
    s,
    "let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,pendingLeaderboardSubmission=null,rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false,rankedTimingIntegrity=null;\n",
    "let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,pendingLeaderboardSubmission=null,rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false,rankedTimingIntegrity=null,rankedStartPromise=null;\n",
    'inline ranked start promise state',
)
s = replace_once(s, helper_old, helper_new, 'inline ticket acquisition helper')

start_old = """function start(challenge=null,skipTutorial=false){if(!skipTutorial&&!challenge&&!save.tutorialSeen){startInteractiveTutorial('run');return}tutorialMode=false;tutorialLocked=false;clearTimeout(tutorialTimer);ui.tutorial.classList.remove('training');try{canvas.focus({preventScroll:true})}catch{try{canvas.focus()}catch{}}activeRunMode=challenge?'challenge':'standard';runCosmeticUnlocks=cosmeticUnlockCount(save);runCosmeticUnlockIds=new Set(cosmeticUnlockedEntries(save).map(x=>x.key));runMastery=newRunMastery();pendingMasteryUnlocks=[];if(challenge&&verifyCompetitiveReplay(challenge)){activeChallenge=JSON.parse(JSON.stringify(challenge));challengeAnalysis=analyzeReplayData(activeChallenge)}else{activeChallenge=null;challengeAnalysis=null}const rankTicket=!challenge?takeLeaderboardTicket():null,seed=activeChallenge?.seed??rankTicket?.seed??freshSeed();activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;rankedRunInvalidReason=null;rankedRunInvalidNoticeShown=false;resetRankedTimingIntegrity();void prefetchLeaderboardTicket();sim.reset(seed,2,6,9);rebuildRenderGeometry();runRecord={version:9,arenaGeneration:2,directorGeneration:6,seed,events:[]};replayData=null;replayIndex=0;replayPaused=false;replaySpeed=1;replayAnalysis=null;lastCompletedReplay=null;transitionSerial++;state='play';paused=false;transition=false;aim=null;activePointerId=null;acc=0;last=performance.now();shownScore=0;scorePulse=0;shake=0;hudMultiplier=1;hudCombo=0;dangerPulse=0;deathImpact=0;visualHoldUntil=0;bounceState.clear();clearFx();hideAll();ui.replayHud.classList.add('hidden');ui.pauseBtn.style.display='block';ui.tutorial.classList.add('hidden');try{ensureAudioCtx();startAmbient();beepStart()}catch(err){captureIssue('audio-start',err)}}
"""
start_new = """function launchRun(challenge=null,skipTutorial=false,rankTicket=null,rankedStartReason=null){tutorialMode=false;tutorialLocked=false;clearTimeout(tutorialTimer);ui.tutorial.classList.remove('training');try{canvas.focus({preventScroll:true})}catch{try{canvas.focus()}catch{}}activeRunMode=challenge?'challenge':'standard';runCosmeticUnlocks=cosmeticUnlockCount(save);runCosmeticUnlockIds=new Set(cosmeticUnlockedEntries(save).map(x=>x.key));runMastery=newRunMastery();pendingMasteryUnlocks=[];if(challenge&&verifyCompetitiveReplay(challenge)){activeChallenge=JSON.parse(JSON.stringify(challenge));challengeAnalysis=analyzeReplayData(activeChallenge)}else{activeChallenge=null;challengeAnalysis=null}const seed=activeChallenge?.seed??rankTicket?.seed??freshSeed();activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;rankedRunInvalidReason=!challenge&&!activeLeaderboardTicket?(rankedStartReason||'LEADERBOARD UNAVAILABLE'):null;rankedRunInvalidNoticeShown=false;resetRankedTimingIntegrity();void prefetchLeaderboardTicket();sim.reset(seed,2,6,9);rebuildRenderGeometry();runRecord={version:9,arenaGeneration:2,directorGeneration:6,seed,events:[]};replayData=null;replayIndex=0;replayPaused=false;replaySpeed=1;replayAnalysis=null;lastCompletedReplay=null;transitionSerial++;state='play';paused=false;transition=false;aim=null;activePointerId=null;acc=0;last=performance.now();shownScore=0;scorePulse=0;shake=0;hudMultiplier=1;hudCombo=0;dangerPulse=0;deathImpact=0;visualHoldUntil=0;bounceState.clear();clearFx();hideAll();ui.replayHud.classList.add('hidden');ui.pauseBtn.style.display='block';ui.tutorial.classList.add('hidden');if(!challenge&&!activeLeaderboardTicket&&rankedRunInvalidReason){rankedRunInvalidNoticeShown=true;showCoach('LOCAL RUN','A global leaderboard ticket was not available for this start.',`Reason: ${rankedRunInvalidReason}. This run still saves locally.`,1500)}try{ensureAudioCtx();startAmbient();beepStart()}catch(err){captureIssue('audio-start',err)}}
async function start(challenge=null,skipTutorial=false){if(!skipTutorial&&!challenge&&!save.tutorialSeen){startInteractiveTutorial('run');return}if(challenge){launchRun(challenge,skipTutorial,null,null);return}if(rankedStartPromise)return rankedStartPromise;state='starting';rankedStartPromise=(async()=>{const acquired=await acquireLeaderboardTicket();if(state!=='starting')return null;launchRun(null,skipTutorial,acquired.ticket,acquired.reason);return acquired})().finally(()=>{rankedStartPromise=null});return rankedStartPromise}
"""
s = replace_once(s, start_old, start_new, 'standard run async acquisition')
index.write_text(s, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old_row = '| VC-008 | MEDIUM | PLAY can consume no leaderboard ticket if asynchronous prefetch has not completed, silently starting an unranked run. | F8 | OPEN |'
new_row = '| VC-008 | MEDIUM | PLAY can consume no leaderboard ticket if asynchronous prefetch has not completed, silently starting an unranked run. | F8 | FIXED — VERIFYING |'
if r.count(old_row) != 1:
    raise SystemExit('VC-008 register marker missing')
r = r.replace(old_row, new_row, 1)
r += '''\n## F8 implementation record — synchronized ranked run start\n\n- Standard PLAY no longer calls `takeLeaderboardTicket()` synchronously while a ticket prefetch may still be in flight.\n- Ranked start acquisition first consumes an already-ready ticket; otherwise it awaits the existing/new ticket request within a bounded 2,000 ms start budget.\n- A successful acquisition uses the server-issued ticket seed for the run exactly as before.\n- If the ticket request settles without a usable ticket, the run starts locally with explicit `LEADERBOARD UNAVAILABLE` status.\n- If the ranked-start budget expires first, the run starts locally with explicit `LEADERBOARD TIMEOUT` status; the still-running prefetch may only prepare a ticket for a later run.\n- While acquisition is pending the lifecycle state is `starting`, preventing cuts/pause/key-repeat starts from treating the not-yet-started run as active gameplay.\n- Repeated standard start attempts share one `rankedStartPromise`, so double-click/Space cannot create parallel ticket acquisitions or multiple runs.\n- Before launch, the async continuation verifies the state is still `starting`; navigation away during the bounded wait cancels that pending launch instead of unexpectedly starting a run later.\n- Mouse PLAY, keyboard Space, standard retry/restart and post-tutorial standard start all converge on the same synchronized `start()` path.\n- Challenge starts bypass ranked-ticket acquisition and remain unchanged.\n- The source client fragment and shipped inline leaderboard runtime now share the same acquisition helper and 2,000 ms contract.\n\nF8 changes only standard-run ticket acquisition/start synchronization and explicit ranked/local status. Physics, scoring, replay format, save schema, ticket TTL, server seed generation and leaderboard verification are unchanged.\n'''
register.write_text(r, encoding='utf-8')
