import fs from 'node:fs';
import assert from 'node:assert/strict';

const html = fs.readFileSync(new URL('../../index.html', import.meta.url), 'utf8');
const source = html.match(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)
  ?.map(x => x.replace(/^<script(?:\s[^>]*)?>/i, '').replace(/<\/script>$/i, ''))
  .sort((a,b)=>b.length-a.length)[0] || '';
assert.ok(source, 'VOIDCUT inline runtime missing');

const fnSource = source.match(/function cosmeticUnlocked\(cat,id,s\)\{[^\n]+\}/)?.[0] || '';
assert.ok(fnSource, 'cosmeticUnlocked helper missing');

const alwaysIds = ['void','aurora','core','reactor','beam','ribbon','pulse','laser','implode','vacuum'];
const alwaysLiteral = "['void','aurora','core','reactor','beam','ribbon','pulse','laser','implode','vacuum'].includes(id)";
assert.ok(fnSource.includes(alwaysLiteral), 'canonical always-unlocked cosmetic set changed');

for (const id of ['aurora','reactor','ribbon','laser','vacuum']) {
  assert.doesNotMatch(fnSource, new RegExp(`if\\(id==='${id}'\\)`), `${id} must not have an unreachable conditional branch after unconditional unlock`);
}

for (const id of ['ember','amethyst','monochrome','hollow','prism','eclipse','comet','echo','sparks','blade','arc','rift','shatter','dissolve','fracture']) {
  assert.match(fnSource, new RegExp(`if\\(id==='${id}'\\)`), `${id} conditional unlock branch must remain`);
}

const cosmeticUnlocked = new Function(`${fnSource}; return cosmeticUnlocked;`)();
const blank = {
  deepestChamber: 1,
  bestScore: 0,
  totalRuns: 0,
  lifetimeCuts: 0,
  lifetimeCloseCalls: 0,
  records: {
    bestMastery:0, largestCut:0, bestBigCutStreak:0, mostNoDividerClears:0,
    fastestClear:null, fewestCutsClear:null, sPlusClears:0, bestSingleCut:0,
  },
};
for (const id of alwaysIds) assert.equal(cosmeticUnlocked('unused', id, blank), true, `${id} must remain always unlocked`);

const conditional = ['ember','amethyst','monochrome','hollow','prism','eclipse','comet','echo','sparks','blade','arc','rift','shatter','dissolve','fracture'];
for (const id of conditional) assert.equal(cosmeticUnlocked('unused', id, blank), false, `${id} must remain locked in a fresh save`);

const progressed = structuredClone(blank);
progressed.deepestChamber = 8;
progressed.bestScore = 250000;
progressed.lifetimeCuts = 250;
progressed.lifetimeCloseCalls = 5;
Object.assign(progressed.records, {
  bestMastery:90,
  largestCut:45,
  bestBigCutStreak:3,
  mostNoDividerClears:3,
  fastestClear:20,
  fewestCutsClear:4,
  sPlusClears:3,
  bestSingleCut:50000,
});
for (const id of conditional) assert.equal(cosmeticUnlocked('unused', id, progressed), true, `${id} threshold behavior must remain intact`);

assert.ok(!html.includes('.vc-screen-cut'), 'obsolete .vc-screen-cut CSS must be fully removed');
for (const token of ['vcCutShell','vcCutBeam','vcCutPaneA','vcCutPaneB']) {
  assert.ok(!html.includes(token), `obsolete ${token} keyframe/reference must be removed`);
}
assert.ok(html.includes('body:has(.toggle[data-setting="reducedMotion"].is-on) .rank-up-fx{display:none!important}'), 'unrelated reduced-motion rank-up suppression must remain');
assert.ok(!html.includes('Signature cut transition. It is intentionally short'), 'dead screen-cut transition comment must be removed');
assert.ok(!html.includes('Screen-cut transition becomes two physical sheets separating.'), 'dead physical screen-cut override comment must be removed');

console.log('F19 dead cosmetic branches and screen-cut CSS regression PASS');
