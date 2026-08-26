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
    "let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,pendingLeaderboardSubmission=null,rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false;",
    "let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,pendingLeaderboardSubmission=null,rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false,rankedTimingIntegrity=null;",
    'leaderboard timing state',
)

replace_once(
    "function invalidateRankedRun(reason='PAUSED'){if(state!=='play'||tutorialMode||!activeLeaderboardTicket)return false;activeLeaderboardTicket=null;rankedRunInvalidReason=String(reason||'PAUSED').toUpperCase();rankedRunInvalidNoticeShown=false;return true}\nfunction updatePauseEligibility(){const el=$('pauseEligibility');if(!el)return;el.textContent=rankedRunInvalidReason?`GLOBAL RANKING DISABLED • ${rankedRunInvalidReason}`:'RUN HELD'}\nfunction showRankedRunInvalidNotice(){if(!rankedRunInvalidReason||rankedRunInvalidNoticeShown||state!=='play')return;rankedRunInvalidNoticeShown=true;showCoach('UNRANKED RUN','Pausing disables global leaderboard eligibility.',`Reason: ${rankedRunInvalidReason}. You can still finish locally.`,1500)}",
    "function invalidateRankedRun(reason='PAUSED'){if(state!=='play'||tutorialMode||!activeLeaderboardTicket)return false;activeLeaderboardTicket=null;rankedRunInvalidReason=String(reason||'PAUSED').toUpperCase();rankedRunInvalidNoticeShown=false;return true}\nconst RANKED_MAX_SINGLE_FRAME_GAP=.20,RANKED_MAX_DISCARDED_TIME=.25;\nfunction rankedTimingActive(){return state==='play'&&!paused&&!transition&&!tutorialMode&&!!activeLeaderboardTicket}\nfunction resetRankedTimingIntegrity(){rankedTimingIntegrity={wallSeconds:0,simBudgetSeconds:0,discardedSeconds:0,timingResets:0,stepLimitHits:0}}\nfunction updatePauseEligibility(){const el=$('pauseEligibility');if(!el)return;el.textContent=rankedRunInvalidReason?`GLOBAL RANKING DISABLED • ${rankedRunInvalidReason}`:'RUN HELD'}\nfunction showRankedRunInvalidNotice(){if(!rankedRunInvalidReason||rankedRunInvalidNoticeShown||state!=='play')return;rankedRunInvalidNoticeShown=true;showCoach('UNRANKED RUN','Global leaderboard eligibility was disabled to preserve competitive timing integrity.',`Reason: ${rankedRunInvalidReason}. You can still finish locally.`,1500)}\nfunction invalidateRankedTiming(reason,notify=true){if(!invalidateRankedRun(reason))return false;if(notify)showRankedRunInvalidNotice();return true}\nfunction trackRankedFrameGap(rawSec,simBudget){if(!rankedTimingActive()||!rankedTimingIntegrity)return;const wall=Math.max(0,Number(rawSec)||0),budget=Math.max(0,Number(simBudget)||0),discarded=Math.max(0,wall-budget);rankedTimingIntegrity.wallSeconds+=wall;rankedTimingIntegrity.simBudgetSeconds+=budget;rankedTimingIntegrity.discardedSeconds+=discarded;if(wall>RANKED_MAX_SINGLE_FRAME_GAP){invalidateRankedTiming('FRAME STALL');return}if(rankedTimingIntegrity.discardedSeconds>=RANKED_MAX_DISCARDED_TIME)invalidateRankedTiming('TIMING DRIFT')}\nfunction trackRankedCatchup(stepLimitHit){if(!stepLimitHit||!rankedTimingActive()||!rankedTimingIntegrity)return;rankedTimingIntegrity.stepLimitHits++;invalidateRankedTiming('CATCH-UP LIMIT')}\nfunction trackRankedTimingReset(reason='TIMING RESET',notify=true,now=performance.now()){if(!rankedTimingActive()||!rankedTimingIntegrity)return;const gap=Math.max(0,(Number(now)-last)/1000),discarded=gap+Math.max(0,acc);rankedTimingIntegrity.timingResets++;rankedTimingIntegrity.wallSeconds+=gap;rankedTimingIntegrity.discardedSeconds+=discarded;if(rankedTimingIntegrity.discardedSeconds>=RANKED_MAX_DISCARDED_TIME)invalidateRankedTiming(reason,notify)}",
    'ranked timing helpers',
)

replace_once(
    "activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;rankedRunInvalidReason=null;rankedRunInvalidNoticeShown=false;void prefetchLeaderboardTicket();sim.reset(seed,2,6,9);",
    "activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;rankedRunInvalidReason=null;rankedRunInvalidNoticeShown=false;resetRankedTimingIntegrity();void prefetchLeaderboardTicket();sim.reset(seed,2,6,9);",
    'run timing reset',
)

replace_once(
    "function update(now){const rawMs=Math.max(.01,now-last),delta=Math.min(rawMs/1000,.05);last=now;const activePlay=state==='play'&&!paused,activeReplay=state==='replay'&&!replayPaused;",
    "function update(now){const rawMs=Math.max(.01,now-last),rawSec=rawMs/1000,delta=Math.min(rawSec,.05);last=now;trackRankedFrameGap(rawSec,delta);const activePlay=state==='play'&&!paused,activeReplay=state==='replay'&&!replayPaused;",
    'main loop frame accounting',
)

replace_once(
    "updateCutHum();stepLimitHit=acc>=DT}sampleRuntime(rawMs,frameSteps,stepLimitHit);",
    "updateCutHum();stepLimitHit=acc>=DT;trackRankedCatchup(stepLimitHit)}sampleRuntime(rawMs,frameSteps,stepLimitHit);",
    'main loop catch-up accounting',
)

replace_once(
    "function resumeLifecycle(){cancelPointerGesture();acc=0;visualBudget=0;last=performance.now();settleViewport(false)}",
    "function resumeLifecycle(){trackRankedTimingReset('LIFECYCLE TIMING RESET');cancelPointerGesture();acc=0;visualBudget=0;last=performance.now();settleViewport(false)}",
    'lifecycle timing reset',
)

replace_once(
    "significant=force||next.o!==prev.o||Math.max(dw,dh)>=.12;viewportState=next;cancelPointerGesture();acc=0;visualBudget=0;last=performance.now();if(significant){if(state==='play'&&!paused){togglePause(true,'DISPLAY CHANGED');",
    "significant=force||next.o!==prev.o||Math.max(dw,dh)>=.12;viewportState=next;trackRankedTimingReset(significant?'DISPLAY CHANGED':'VIEWPORT TIMING RESET',!significant);cancelPointerGesture();acc=0;visualBudget=0;last=performance.now();if(significant){if(state==='play'&&!paused){togglePause(true,'DISPLAY CHANGED');",
    'viewport timing reset',
)

index.write_text(s, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old = '| VC-003 | CRITICAL | Main-loop frame-gap clamping can create a slow-motion competitive advantage under throttling/stalls. | F3 | OPEN |'
new = '| VC-003 | CRITICAL | Main-loop frame-gap clamping can create a slow-motion competitive advantage under throttling/stalls. | F3 | FIXED — VERIFYING |'
if r.count(old) != 1:
    raise SystemExit('VC-003 register marker missing')
r = r.replace(old, new, 1)
r += '''\n## F3 implementation record — ranked wall-clock integrity\n\n- Ranked standard PLAY now maintains an explicit runtime timing-integrity ledger separate from deterministic simulation state.\n- Active-play frame wall time is compared against the bounded simulation delta; discarded wall time is accumulated rather than silently ignored.\n- Any active-play frame gap greater than 200 ms immediately invalidates global leaderboard eligibility as `FRAME STALL`.\n- Cumulative discarded active-play wall time of 250 ms or more invalidates eligibility as `TIMING DRIFT`, preventing repeated smaller throttling gaps from accumulating a meaningful reaction-time advantage.\n- Any ranked main-loop catch-up step-cap hit invalidates eligibility as `CATCH-UP LIMIT`.\n- Lifecycle and viewport timing resets debit unsimulated wall time plus pending accumulator time into the same discarded-time budget before clocks are reset.\n- Significant display changes retain the F2 pause invalidation path; insignificant repeated viewport resets can no longer erase simulation time indefinitely without eventually becoming unranked.\n- Intentional chamber transitions, paused runs, tutorial/challenge/replay states and already-unranked runs are excluded from ranked timing accounting.\n- Timing invalidation discards the active leaderboard ticket but leaves the run fully playable and recordable locally.\n\nF3 does not alter simulation speed, physics, scoring, replay format or save schema. It only determines whether a locally playable standard run remains eligible for global submission.\n'''
register.write_text(r, encoding='utf-8')
