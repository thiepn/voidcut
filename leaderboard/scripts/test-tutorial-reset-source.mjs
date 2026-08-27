import fs from 'node:fs';
import assert from 'node:assert/strict';

const html = fs.readFileSync(new URL('../../index.html', import.meta.url), 'utf8');
const source = html.match(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)
  ?.map(x => x.replace(/^<script(?:\s[^>]*)?>/i, '').replace(/<\/script>$/i, ''))
  .sort((a,b)=>b.length-a.length)[0] || '';
assert.ok(source, 'VOIDCUT inline runtime missing');

const configureSource = source.match(/function configureTutorialStage\(stage,step=null\)\{[^\n]+\}/)?.[0] || '';
assert.ok(configureSource, 'configureTutorialStage helper missing');
assert.ok(configureSource.includes('sim.reset(seed,2,4,9);'), 'tutorial stage must begin from canonical Sim.reset with arena2/director4/scoring9');
assert.ok(configureSource.indexOf('sim.reset(seed,2,4,9);') < configureSource.indexOf('const a=tutorialArena();'), 'canonical reset must happen before tutorial geometry is installed');
for (const token of [
  'sim.previousArena=null;',
  'sim.previousStyle=null;',
  'sim.previousTempo=null;',
  'sim.previousPressure=null;',
  'sim.previousModifier=null;',
  'sim.briefingRemaining=0;',
  'sim.modifierTick=-1;',
]) assert.ok(configureSource.includes(token), `tutorial generation reset missing: ${token}`);
assert.doesNotMatch(configureSource, /sim\.runElapsed=0;/, 'tutorial setup should rely on canonical reset for run clock rather than partial manual reset');
assert.doesNotMatch(configureSource, /sim\.score=0;/, 'tutorial setup should rely on canonical reset for scoring state rather than partial manual reset');

const order=[];
let resetCalls=0;
const sim={
  arenaGen:99,directorGen:99,scoringVersion:77,seed:123,runElapsed:88,chamber:41,score:999999,
  success:9,dividers:8,largest:777,totalRemoved:666,previousArena:'dirty-arena',previousStyle:'dirty-style',
  previousTempo:'dirty-tempo',previousPressure:12,previousModifier:'dirty-modifier',closestCall:1,closeCalls:8,
  bestSingleCut:999,fewestClear:1,fastestClear:2,masteryBonus:99,bestMastery:99,sPlusClears:8,
  currentBigCutStreak:7,bestBigCutStreak:9,noDividerClears:5,chamberCloseCalls:4,highestNoCloseCallChamber:33,
  nextR:99,nextB:99,briefingRemaining:9.5,modifierTick:88,cut:{dirty:true},regions:[{dirty:true}],balls:[{dirty:true}],
  reset(seed,arenaGen,directorGen,scoringVersion){
    order.push('reset'); resetCalls++;
    Object.assign(this,{
      arenaGen,directorGen,scoringVersion,seed,runElapsed:0,chamber:1,score:0,success:0,dividers:0,largest:0,totalRemoved:0,
      previousArena:null,previousStyle:null,previousTempo:null,previousPressure:null,previousModifier:null,closestCall:Infinity,
      closeCalls:0,bestSingleCut:0,fewestClear:Infinity,fastestClear:Infinity,masteryBonus:0,bestMastery:0,sPlusClears:0,
      currentBigCutStreak:0,bestBigCutStreak:0,noDividerClears:0,chamberCloseCalls:0,highestNoCloseCallChamber:0,
      nextR:1,nextB:1,briefingRemaining:0,modifierTick:-1,cut:null,regions:[{fromReset:true}],balls:[{fromReset:true}],
    });
  }
};
class RNG { constructor(seed){this.seed=seed>>>0;} }
const AX=10,AY=20,AW=600,AH=900,BALL_R=12;
let tutorialTimer=1,tutorialLocked=true,tutorialStage=0,tutorialStep='dirty';
let shownScore=123,hudMultiplier=9,hudCombo=9,acc=.5,last=1;
const clearTimeout=()=>{};
const performance={now:()=>4321};
const tutorialArena=()=>{order.push('arena');return{type:'rectangle',label:'TRAINING',v:[{x:10,y:20},{x:610,y:20},{x:610,y:920},{x:10,y:920}],area:540000,risk:1,generation:2};};
const tutorialCore=(id,x,y,region=1)=>({id,pos:{x,y},prev:{x,y},vel:{x:0,y:0},r:BALL_R,region,bump:0,type:'standard',baseSpeed:0,pulsePhase:0});
let rebuilds=0,fxClears=0,prompts=0,bounceClears=0;
const rebuildRenderGeometry=()=>{rebuilds++;};
const clearFx=()=>{fxClears++;};
const refreshTutorialPrompt=()=>{prompts++;};
const bounceState={clear:()=>{bounceClears++;}};

const factory = new Function(
  'sim','RNG','AX','AY','AW','AH','BALL_R','tutorialArena','tutorialCore','rebuildRenderGeometry','clearFx','refreshTutorialPrompt','bounceState','performance','clearTimeout',
  `let tutorialTimer=1,tutorialLocked=true,tutorialStage=0,tutorialStep='dirty',shownScore=123,hudMultiplier=9,hudCombo=9,acc=.5,last=1;\n${configureSource}\nreturn{run:(stage,step=null)=>configureTutorialStage(stage,step),get:()=>({tutorialLocked,tutorialStage,tutorialStep,shownScore,hudMultiplier,hudCombo,acc,last})};`
)(sim,RNG,AX,AY,AW,AH,BALL_R,tutorialArena,tutorialCore,rebuildRenderGeometry,clearFx,refreshTutorialPrompt,bounceState,performance,clearTimeout);

factory.run(2);
assert.equal(resetCalls,1,'tutorial lesson must invoke canonical reset exactly once');
assert.deepEqual(order.slice(0,2),['reset','arena'],'reset must precede training arena installation');
assert.equal(sim.seed,0x47C002);
assert.equal(sim.arenaGen,2);
assert.equal(sim.directorGen,4);
assert.equal(sim.scoringVersion,9);
assert.equal(sim.runElapsed,0);
assert.equal(sim.score,0);
assert.equal(sim.success,0);
assert.equal(sim.dividers,0);
assert.equal(sim.largest,0);
assert.equal(sim.totalRemoved,0);
assert.equal(sim.closestCall,Infinity);
assert.equal(sim.closeCalls,0);
assert.equal(sim.bestSingleCut,0);
assert.equal(sim.fewestClear,Infinity);
assert.equal(sim.fastestClear,Infinity);
assert.equal(sim.masteryBonus,0);
assert.equal(sim.bestMastery,0);
assert.equal(sim.sPlusClears,0);
assert.equal(sim.currentBigCutStreak,0);
assert.equal(sim.bestBigCutStreak,0);
assert.equal(sim.noDividerClears,0);
assert.equal(sim.highestNoCloseCallChamber,0);
assert.equal(sim.previousArena,null);
assert.equal(sim.previousStyle,null);
assert.equal(sim.previousTempo,null);
assert.equal(sim.previousPressure,null);
assert.equal(sim.previousModifier,null);
assert.equal(sim.briefingRemaining,0,'tutorial must never inherit a modifier/milestone briefing gate');
assert.equal(sim.modifierTick,-1);
assert.equal(sim.chamber,2);
assert.equal(sim.cut,null);
assert.equal(sim.regions.length,1);
assert.equal(sim.regions[0].id,1);
assert.equal(sim.balls.length,2);
assert.deepEqual(sim.balls.map(b=>b.id),[1,2]);
assert.equal(sim.nextR,2);
assert.equal(sim.nextB,10);
assert.equal(sim.chamberCuts,0);
assert.equal(sim.chamberElapsed,0);
assert.equal(sim.chamberRemovalCuts,0);
assert.equal(sim.chamberDividerCuts,0);
assert.equal(sim.chamberRemovedPct,0);
assert.equal(sim.chamberCloseCalls,0);
assert.equal(sim.plan.directorGen,4);
assert.equal(sim.plan.style,'training');
assert.equal(sim.plan.tempo,'breather');
assert.equal(sim.plan.flow,'TRAINING');
assert.equal(factory.get().tutorialStage,2);
assert.equal(factory.get().tutorialStep,'setupDivider');
assert.equal(factory.get().tutorialLocked,false);
assert.equal(factory.get().shownScore,0);
assert.equal(factory.get().hudMultiplier,1);
assert.equal(factory.get().hudCombo,0);
assert.equal(factory.get().acc,0);
assert.equal(factory.get().last,4321);
assert.equal(rebuilds,1);
assert.equal(fxClears,1);
assert.equal(bounceClears,1);
assert.equal(prompts,1);

// Retry/next-stage calls must reset again rather than inheriting the prior lesson state.
sim.score=12345;sim.runElapsed=55;sim.briefingRemaining=7;sim.previousModifier='leak';sim.cut={leak:true};
factory.run(2,'setupCollapse');
assert.equal(resetCalls,2,'tutorial retry must invoke canonical reset again');
assert.equal(sim.score,0);
assert.equal(sim.runElapsed,0);
assert.equal(sim.briefingRemaining,0);
assert.equal(sim.previousModifier,null);
assert.equal(sim.cut,null);
assert.equal(factory.get().tutorialStep,'setupCollapse');

assert.ok(source.includes("tutorialTimer=setTimeout(()=>{if(!tutorialMode)return;configureTutorialStage(tutorialStage,tutorialStep)},950)"), 'tutorial retry must continue through configureTutorialStage');
assert.ok(source.includes("tutorialTimer=setTimeout(()=>{if(!tutorialMode)return;configureTutorialStage(stage)},720)"), 'tutorial lesson transition must continue through configureTutorialStage');
assert.ok(source.includes("tutorialTimer=setTimeout(()=>{if(!tutorialMode)return;state='play';configureTutorialStage(tutorialStage,tutorialStep)},950)"), 'tutorial death retry must continue through configureTutorialStage');

console.log('F18 tutorial full-reset regression PASS');
