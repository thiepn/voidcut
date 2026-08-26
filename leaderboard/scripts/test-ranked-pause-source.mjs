import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const indexPath = path.resolve(process.argv[2] || '../index.html');
const html = fs.readFileSync(indexPath, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)].map(m => m[1]);
assert.ok(scripts.length, 'VOIDCUT inline runtime was not found');
const source = scripts.sort((a,b)=>b.length-a.length)[0];

const helperMatch = source.match(/function invalidateRankedRun\(reason='PAUSED'\)\{[^\n]+\}/);
assert.ok(helperMatch, 'invalidateRankedRun helper missing');
const makeHelper = new Function(`
  let state='play', tutorialMode=false, activeLeaderboardTicket={ticketId:'t'}, rankedRunInvalidReason=null, rankedRunInvalidNoticeShown=true;
  ${helperMatch[0]};
  return {
    run:(reason)=>invalidateRankedRun(reason),
    get:()=>({state,tutorialMode,activeLeaderboardTicket,rankedRunInvalidReason,rankedRunInvalidNoticeShown}),
    set:(x)=>{if('state'in x)state=x.state;if('tutorialMode'in x)tutorialMode=x.tutorialMode;if('activeLeaderboardTicket'in x)activeLeaderboardTicket=x.activeLeaderboardTicket;if('rankedRunInvalidReason'in x)rankedRunInvalidReason=x.rankedRunInvalidReason;if('rankedRunInvalidNoticeShown'in x)rankedRunInvalidNoticeShown=x.rankedRunInvalidNoticeShown;}
  };
`);
const h = makeHelper();
assert.equal(h.run('APP SUSPENDED'), true);
assert.equal(h.get().activeLeaderboardTicket, null);
assert.equal(h.get().rankedRunInvalidReason, 'APP SUSPENDED');
assert.equal(h.get().rankedRunInvalidNoticeShown, false);
h.set({state:'menu',activeLeaderboardTicket:{ticketId:'x'},rankedRunInvalidReason:null});
assert.equal(h.run('PAUSED'), false, 'non-play states must not mutate leaderboard eligibility');
assert.ok(h.get().activeLeaderboardTicket, 'non-play ticket should remain untouched');
h.set({state:'play',tutorialMode:true,activeLeaderboardTicket:{ticketId:'x'}});
assert.equal(h.run('PAUSED'), false, 'tutorial must not be treated as ranked');
h.set({tutorialMode:false,activeLeaderboardTicket:null});
assert.equal(h.run('PAUSED'), false, 'already-unranked run should be a no-op');

for (const required of [
  "if(willPause&&!paused)invalidateRankedRun(pauseReason)",
  "togglePause(true,'APP SUSPENDED')",
  "togglePause(true,'DISPLAY CHANGED')",
  "rankedRunInvalidReason=null;rankedRunInvalidNoticeShown=false;void prefetchLeaderboardTicket()",
  "const leaderboardTicketForRun=activeLeaderboardTicket,rankedInvalidReasonForRun=rankedRunInvalidReason",
  "const rankedText=rankedInvalidReasonForRun?`UNRANKED • ${rankedInvalidReasonForRun}`:''",
  'id="pauseEligibility"',
]) assert.ok(source.includes(required), `missing F2 invariant: ${required}`);

const toggle = source.match(/function togglePause\(force,pauseReason='PAUSED'\)\{[^\n]+\}/)?.[0] || '';
assert.ok(toggle.includes('invalidateRankedRun(pauseReason)'), 'manual pause path must invalidate ranked ticket');
assert.ok(toggle.indexOf('invalidateRankedRun(pauseReason)') < toggle.indexOf('paused=willPause'), 'ticket must be invalidated before pause state is committed');

console.log('F2 ranked pause source regression PASS');
