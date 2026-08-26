from pathlib import Path

root = Path(__file__).resolve().parents[2]
index = root / 'index.html'
register = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'

s = index.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    s = s.replace(old, new, 1)

replace_once(
    "let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,pendingLeaderboardSubmission=null;",
    "let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,pendingLeaderboardSubmission=null,rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false;",
    'leaderboard state',
)

replace_once(
    "function takeLeaderboardTicket(){if(!leaderboardTicket||leaderboardTicket.expiresAt<=Date.now()+1000){leaderboardTicket=null;return null}const t=leaderboardTicket;leaderboardTicket=null;return t}",
    "function takeLeaderboardTicket(){if(!leaderboardTicket||leaderboardTicket.expiresAt<=Date.now()+1000){leaderboardTicket=null;return null}const t=leaderboardTicket;leaderboardTicket=null;return t}\nfunction invalidateRankedRun(reason='PAUSED'){if(state!=='play'||tutorialMode||!activeLeaderboardTicket)return false;activeLeaderboardTicket=null;rankedRunInvalidReason=String(reason||'PAUSED').toUpperCase();rankedRunInvalidNoticeShown=false;return true}\nfunction updatePauseEligibility(){const el=$('pauseEligibility');if(!el)return;el.textContent=rankedRunInvalidReason?`GLOBAL RANKING DISABLED • ${rankedRunInvalidReason}`:'RUN HELD'}\nfunction showRankedRunInvalidNotice(){if(!rankedRunInvalidReason||rankedRunInvalidNoticeShown||state!=='play')return;rankedRunInvalidNoticeShown=true;showCoach('UNRANKED RUN','Pausing disables global leaderboard eligibility.',`Reason: ${rankedRunInvalidReason}. You can still finish locally.`,1500)}",
    'ranked invalidation helper',
)

replace_once(
    "activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;void prefetchLeaderboardTicket();sim.reset(seed,2,6,9);",
    "activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;rankedRunInvalidReason=null;rankedRunInvalidNoticeShown=false;void prefetchLeaderboardTicket();sim.reset(seed,2,6,9);",
    'run reset',
)

replace_once(
    "function togglePause(force){if(state!=='play')return;if(transition&&force!==true)return;paused=force===true?true:!paused;aim=null;activePointerId=null;if(paused){stopCutHum();ui.pause.classList.remove('hidden');ui.tutorial.classList.add('hidden')}else{ui.pause.classList.add('hidden');acc=0;last=performance.now();ensureAudioCtx();updateAmbient();if(tutorialMode)refreshTutorialPrompt()}}",
    "function togglePause(force,pauseReason='PAUSED'){if(state!=='play')return;if(transition&&force!==true)return;const willPause=force===true?true:!paused;if(willPause&&!paused)invalidateRankedRun(pauseReason);paused=willPause;aim=null;activePointerId=null;if(paused){stopCutHum();updatePauseEligibility();ui.pause.classList.remove('hidden');ui.tutorial.classList.add('hidden')}else{ui.pause.classList.add('hidden');acc=0;last=performance.now();ensureAudioCtx();updateAmbient();showRankedRunInvalidNotice();if(tutorialMode)refreshTutorialPrompt()}}",
    'togglePause',
)

replace_once(
    "function suspendLifecycle(){if(state==='play'&&!paused)togglePause(true);if(state==='replay'&&!replayPaused){replayPaused=true;$('replayPause').textContent='RESUME'}cancelPointerGesture();stopCutHum();acc=0;visualBudget=0;try{if(audio?.state==='running')audio.suspend()}catch{}}",
    "function suspendLifecycle(){if(state==='play'&&!paused)togglePause(true,'APP SUSPENDED');if(state==='replay'&&!replayPaused){replayPaused=true;$('replayPause').textContent='RESUME'}cancelPointerGesture();stopCutHum();acc=0;visualBudget=0;try{if(audio?.state==='running')audio.suspend()}catch{}}",
    'lifecycle pause',
)

replace_once(
    "if(significant){if(state==='play'&&!paused){togglePause(true);showCoach('DISPLAY CHANGED','Run paused so touch coordinates stay stable.','Resume when ready.',1200)}",
    "if(significant){if(state==='play'&&!paused){togglePause(true,'DISPLAY CHANGED');showCoach('DISPLAY CHANGED','Run paused so touch coordinates stay stable.','Global ranking is disabled for this run.',1200)}",
    'viewport pause',
)

replace_once(
    '<div class="pause-footer">RUN HELD</div>',
    '<div id="pauseEligibility" class="pause-footer">RUN HELD</div>',
    'pause eligibility UI',
)

replace_once(
    "const leaderboardTicketForRun=activeLeaderboardTicket;activeLeaderboardTicket=null;if(completed&&leaderboardTicketForRun)queueLeaderboardSubmission(completed,leaderboardTicketForRun);",
    "const leaderboardTicketForRun=activeLeaderboardTicket,rankedInvalidReasonForRun=rankedRunInvalidReason;activeLeaderboardTicket=null;if(completed&&leaderboardTicketForRun)queueLeaderboardSubmission(completed,leaderboardTicketForRun);",
    'result ticket capture',
)

replace_once(
    "ui.newBest.textContent=[duelText,...newRecords].filter(Boolean).slice(0,3).join(' • ');",
    "const rankedText=rankedInvalidReasonForRun?`UNRANKED • ${rankedInvalidReasonForRun}`:'';ui.newBest.textContent=[rankedText,duelText,...newRecords].filter(Boolean).slice(0,3).join(' • ');",
    'result unranked status',
)

index.write_text(s, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old = '| VC-002 | CRITICAL | Ranked runs can be manually paused or lifecycle-paused without losing leaderboard eligibility. | F2 | OPEN |'
new = '| VC-002 | CRITICAL | Ranked runs can be manually paused or lifecycle-paused without losing leaderboard eligibility. | F2 | FIXED — VERIFYING |'
if r.count(old) != 1:
    raise SystemExit('VC-002 register marker missing')
r = r.replace(old, new, 1)
r += '''\n## F2 implementation record — ranked pause invalidation\n\n- Global leaderboard eligibility is now fail-closed on the first pause of a ticketed standard PLAY run.\n- Manual pause, keyboard pause, pause-button use, browser/app suspension, tab visibility loss, pagehide/freeze, and significant display-change pauses all converge on the same invalidation path.\n- Invalidation immediately discards the active leaderboard ticket, so the completed replay cannot enter the submission queue.\n- The run remains playable locally after invalidation; local records, replay export, progression and retry behavior are preserved.\n- Tutorial, challenge and replay pause behavior is unchanged because they never own a global leaderboard ticket.\n- Each new standard run resets the invalidation state and may use a fresh prefetched ticket normally.\n- The pause sheet and final result explicitly disclose when the current run became unranked.\n\nF2 changes are limited to leaderboard eligibility around pause/lifecycle interruption. Simulation timing hardening remains reserved for F3.\n'''
register.write_text(r, encoding='utf-8')
