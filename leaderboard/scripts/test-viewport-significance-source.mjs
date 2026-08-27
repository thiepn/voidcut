import fs from 'node:fs';
import assert from 'node:assert/strict';

const html = fs.readFileSync(new URL('../../index.html', import.meta.url), 'utf8');
const source = html.match(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)
  ?.map(x => x.replace(/^<script(?:\s[^>]*)?>/i, '').replace(/<\/script>$/i, ''))
  .sort((a,b)=>b.length-a.length)[0] || '';
assert.ok(source, 'VOIDCUT inline runtime missing');

const settleSource = source.match(/function settleViewport\(force=false\)\{[^\n]+\}/)?.[0] || '';
assert.ok(settleSource, 'settleViewport helper missing');
assert.ok(settleSource.includes("significant=force||next.o!==prev.o||Math.max(dw,dh)>=.12"), 'existing 12%/orientation/force significance rule must remain');
assert.ok(settleSource.includes("viewportState=next;if(significant){trackRankedTimingReset('DISPLAY CHANGED');cancelPointerGesture();acc=0;visualBudget=0;last=performance.now();"), 'all destructive timing/input reset work must begin only after significance is true');
assert.ok(!settleSource.includes('VIEWPORT TIMING RESET'), 'insignificant viewport events must not consume ranked timing-reset budget');
assert.ok(!/viewportState=next;trackRankedTimingReset/.test(settleSource), 'timing reset must not run unconditionally after viewport synchronization');
assert.ok(!/viewportState=next;cancelPointerGesture/.test(settleSource), 'gesture cancellation must not run unconditionally after viewport synchronization');

for (const listener of [
  "window.addEventListener('resize',()=>settleViewport())",
  "window.addEventListener('orientationchange',()=>settleViewport(true))",
  "window.visualViewport?.addEventListener('resize',()=>settleViewport())",
  "window.visualViewport?.addEventListener('scroll',()=>settleViewport())",
]) assert.ok(source.includes(listener), `viewport listener contract missing: ${listener}`);

function makeHarness({initial={w:400,h:800,o:'portrait'}, next={w:400,h:800,o:'portrait'}, state='play', paused=false, replayPaused=false}={}) {
  let viewportState = {...initial};
  let viewportTimer = 0;
  let acc = .087;
  let visualBudget = .42;
  let last = 1234;
  let activePointerId = 7;
  let aim = {o:{x:10,y:20},p:{x:30,y:40}};
  let timingResets = 0;
  let timingReason = null;
  let cancels = 0;
  let pauses = 0;
  let coaches = 0;
  let refreshes = 0;
  let fitCalls = 0;
  const replayPauseButton = {textContent:'PAUSE'};
  const performance = {now:()=>9000};
  const clearTimeout = () => {};
  const setTimeout = fn => { fn(); return 1; };
  function fitViewport(){fitCalls++; return {...next};}
  function trackRankedTimingReset(reason){timingResets++;timingReason=reason;}
  function cancelPointerGesture(){cancels++;activePointerId=null;aim=null;}
  function togglePause(force,reason){assert.equal(force,true);assert.equal(reason,'DISPLAY CHANGED');pauses++;paused=true;}
  function showCoach(){coaches++;}
  function refreshFullscreen(){refreshes++;}
  function $(id){assert.equal(id,'replayPause');return replayPauseButton;}

  const api = new Function(
    'initialState','initialTimer','initialAcc','initialVisualBudget','initialLast','initialPointer','initialAim','initialReplayPaused',
    'fitViewport','trackRankedTimingReset','cancelPointerGesture','togglePause','showCoach','refreshFullscreen','$','performance','clearTimeout','setTimeout','state','initialPaused',
    `let viewportState=initialState,viewportTimer=initialTimer,acc=initialAcc,visualBudget=initialVisualBudget,last=initialLast,activePointerId=initialPointer,aim=initialAim,replayPaused=initialReplayPaused,paused=initialPaused;\n${settleSource}\nreturn{run:(force=false)=>settleViewport(force),get:()=>({viewportState,viewportTimer,acc,visualBudget,last,activePointerId,aim,replayPaused,paused})};`
  )(
    viewportState, viewportTimer, acc, visualBudget, last, activePointerId, aim, replayPaused,
    fitViewport, trackRankedTimingReset, cancelPointerGesture, togglePause, showCoach, refreshFullscreen, $, performance, clearTimeout, setTimeout, state, paused,
  );

  return {api, counts:()=>({timingResets,timingReason,cancels,pauses,coaches,refreshes,fitCalls}), replayPauseButton};
}

{
  const h=makeHarness({initial:{w:400,h:800,o:'portrait'},next:{w:420,h:790,o:'portrait'}}); // max delta 5%
  h.api.run(false);
  const s=h.api.get(), c=h.counts();
  assert.deepEqual(s.viewportState,{w:420,h:790,o:'portrait'},'insignificant event must still synchronize viewport state');
  assert.equal(c.fitCalls,1,'existing viewport state should require one new fit pass');
  assert.equal(c.timingResets,0,'insignificant viewport movement must not reset ranked timing');
  assert.equal(c.cancels,0,'insignificant viewport movement must not cancel active gesture');
  assert.equal(c.pauses,0,'insignificant viewport movement must not pause play');
  assert.equal(s.activePointerId,7,'active pointer must survive insignificant viewport movement');
  assert.ok(s.aim,'aim gesture must survive insignificant viewport movement');
  assert.equal(s.acc,.087,'simulation accumulator must survive insignificant viewport movement');
  assert.equal(s.visualBudget,.42,'visual budget must survive insignificant viewport movement');
  assert.equal(s.last,1234,'frame timestamp must survive insignificant viewport movement');
  assert.equal(c.refreshes,1,'fullscreen state still refreshes after viewport synchronization');
}

{
  const h=makeHarness({initial:{w:400,h:800,o:'portrait'},next:{w:500,h:800,o:'portrait'}}); // 25%
  h.api.run(false);
  const s=h.api.get(), c=h.counts();
  assert.equal(c.timingResets,1,'significant viewport change must retain ranked timing accounting');
  assert.equal(c.timingReason,'DISPLAY CHANGED');
  assert.equal(c.cancels,1,'significant viewport change must cancel active gesture');
  assert.equal(s.activePointerId,null);
  assert.equal(s.aim,null);
  assert.equal(s.acc,0);
  assert.equal(s.visualBudget,0);
  assert.equal(s.last,9000);
  assert.equal(c.pauses,1,'significant viewport change must pause active play');
  assert.equal(s.paused,true);
  assert.equal(c.coaches,1,'significant viewport change should retain explanatory UI');
}

{
  const h=makeHarness({initial:{w:400,h:800,o:'portrait'},next:{w:401,h:799,o:'portrait'}});
  h.api.run(true);
  const c=h.counts();
  assert.equal(c.timingResets,1,'forced viewport change must be significant even with tiny dimension delta');
  assert.equal(c.cancels,1);
  assert.equal(c.pauses,1);
}

{
  const h=makeHarness({initial:{w:400,h:800,o:'portrait'},next:{w:800,h:400,o:'landscape'},state:'replay',replayPaused:false});
  h.api.run(false);
  const s=h.api.get(), c=h.counts();
  assert.equal(c.pauses,0,'replay significance must not call gameplay togglePause');
  assert.equal(s.replayPaused,true,'significant viewport change must pause active replay');
  assert.equal(h.replayPauseButton.textContent,'RESUME');
  assert.equal(c.cancels,1);
}

console.log('F17 viewport significance/input preservation regression PASS');
