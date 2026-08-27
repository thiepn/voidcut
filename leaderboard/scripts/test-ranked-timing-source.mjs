import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const indexPath = path.resolve(process.argv[2] || '../index.html');
const html = fs.readFileSync(indexPath, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
assert.ok(scripts.length, 'VOIDCUT inline runtime was not found');
const source = scripts.sort((a,b)=>b.length-a.length)[0];

const grab = (name) => {
  const m = source.match(new RegExp(`function ${name}\\([^\\n]+`));
  assert.ok(m, `${name} helper missing`);
  return m[0];
};
const constants = source.match(/const RANKED_MAX_SINGLE_FRAME_GAP=[^;]+,RANKED_MAX_DISCARDED_TIME=[^;]+;/)?.[0];
assert.ok(constants, 'ranked timing constants missing');

const helpers = [
  'rankedTimingActive',
  'resetRankedTimingIntegrity',
  'invalidateRankedTiming',
  'trackRankedFrameGap',
  'trackRankedCatchup',
  'trackRankedTimingReset',
].map(grab).join('\n');

const makeHarness = () => new Function(`
  let state='play',paused=false,transition=false,tutorialMode=false;
  let activeLeaderboardTicket={ticketId:'ranked'},rankedTimingIntegrity=null;
  let rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false;
  let last=0,acc=0,notices=0;
  function invalidateRankedRun(reason='PAUSED'){
    if(state!=='play'||tutorialMode||!activeLeaderboardTicket)return false;
    activeLeaderboardTicket=null;
    rankedRunInvalidReason=String(reason||'PAUSED').toUpperCase();
    rankedRunInvalidNoticeShown=false;
    return true;
  }
  function showRankedRunInvalidNotice(){notices++}
  ${constants}
  ${helpers}
  resetRankedTimingIntegrity();
  return {
    frame:(raw,budget)=>trackRankedFrameGap(raw,budget),
    catchup:(hit)=>trackRankedCatchup(hit),
    reset:(reason,notify,now)=>trackRankedTimingReset(reason,notify,now),
    get:()=>({state,paused,transition,tutorialMode,activeLeaderboardTicket,rankedTimingIntegrity,rankedRunInvalidReason,notices,last,acc}),
    set:(x)=>{
      if('state'in x)state=x.state;
      if('paused'in x)paused=x.paused;
      if('transition'in x)transition=x.transition;
      if('tutorialMode'in x)tutorialMode=x.tutorialMode;
      if('activeLeaderboardTicket'in x)activeLeaderboardTicket=x.activeLeaderboardTicket;
      if('rankedRunInvalidReason'in x)rankedRunInvalidReason=x.rankedRunInvalidReason;
      if('last'in x)last=x.last;
      if('acc'in x)acc=x.acc;
    },
    fresh:()=>{activeLeaderboardTicket={ticketId:'ranked'};rankedRunInvalidReason=null;notices=0;resetRankedTimingIntegrity();}
  };
`)();

{
  const h = makeHarness();
  for(let i=0;i<600;i++) h.frame(1/60,1/60);
  assert.ok(h.get().activeLeaderboardTicket, 'smooth ranked play must remain eligible');
  assert.equal(h.get().rankedTimingIntegrity.discardedSeconds, 0);
}

{
  const h = makeHarness();
  h.frame(.12,.05);
  assert.ok(h.get().activeLeaderboardTicket, 'one moderate frame stutter should remain inside tolerance');
  assert.ok(h.get().rankedTimingIntegrity.discardedSeconds > .069 && h.get().rankedTimingIntegrity.discardedSeconds < .071);
}

{
  const h = makeHarness();
  h.frame(.21,.05);
  assert.equal(h.get().activeLeaderboardTicket, null, 'single >200ms gap must invalidate ranking');
  assert.equal(h.get().rankedRunInvalidReason, 'FRAME STALL');
  assert.equal(h.get().notices, 1);
}

{
  const h = makeHarness();
  for(let i=0;i<4;i++) h.frame(.10,.05);
  assert.ok(h.get().activeLeaderboardTicket, '200ms cumulative discarded time remains below threshold');
  h.frame(.10,.05);
  assert.equal(h.get().activeLeaderboardTicket, null, '250ms cumulative discarded time must invalidate ranking');
  assert.equal(h.get().rankedRunInvalidReason, 'TIMING DRIFT');
}

{
  const h = makeHarness();
  h.catchup(true);
  assert.equal(h.get().activeLeaderboardTicket, null, 'catch-up cap hit must invalidate ranking');
  assert.equal(h.get().rankedRunInvalidReason, 'CATCH-UP LIMIT');
}

{
  const h = makeHarness();
  h.set({last:1000,acc:.005});
  h.reset('VIEWPORT TIMING RESET',true,1100);
  assert.ok(h.get().activeLeaderboardTicket, 'small timing reset loss should remain inside tolerance');
  assert.ok(h.get().rankedTimingIntegrity.discardedSeconds > .104 && h.get().rankedTimingIntegrity.discardedSeconds < .106);
  h.set({last:1100,acc:.005});
  h.reset('VIEWPORT TIMING RESET',true,1250);
  assert.equal(h.get().activeLeaderboardTicket, null, 'repeated timing resets must consume the same discarded-time budget');
  assert.equal(h.get().rankedRunInvalidReason, 'VIEWPORT TIMING RESET');
}

{
  const h = makeHarness();
  h.set({transition:true});
  h.frame(.5,.05);
  assert.ok(h.get().activeLeaderboardTicket, 'intentional transitions must be excluded from active-play timing enforcement');
  h.set({transition:false,paused:true});
  h.frame(.5,.05);
  assert.ok(h.get().activeLeaderboardTicket, 'paused state must be excluded from timing enforcement');
}

for (const required of [
  'trackRankedFrameGap(rawSec,delta)',
  'trackRankedCatchup(stepLimitHit)',
  "trackRankedTimingReset('LIFECYCLE TIMING RESET')",
  "if(significant){trackRankedTimingReset('DISPLAY CHANGED')",
  'resetRankedTimingIntegrity();void prefetchLeaderboardTicket()',
  "invalidateRankedTiming('FRAME STALL',notify)",
  "invalidateRankedTiming('TIMING DRIFT',notify)",
  "invalidateRankedTiming('CATCH-UP LIMIT',notify)",
]) assert.ok(source.includes(required), `missing F3 invariant: ${required}`);

console.log('F3 ranked timing source regression PASS');
