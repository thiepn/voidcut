import fs from 'node:fs';
import assert from 'node:assert/strict';

const worker = fs.readFileSync(new URL('../src/index.js', import.meta.url), 'utf8');

const handlers = [
  ['createProfile', /return await createProfile\(request, env\);/],
  ['startRun', /return await startRun\(request, env\);/],
  ['forwardSubmission', /return await forwardSubmission\(request, env, ticketId\);/],
  ['leaderboard', /return await leaderboard\(request, env\);/],
  ['replayResponse', /return await replayResponse\(request, env, url\.pathname\.slice\('\/replay\/'\.length\)\.toLowerCase\(\)\);/],
];

for (const [name, pattern] of handlers) {
  assert.match(worker, new RegExp(`async function ${name}\\b`), `${name} must remain async`);
  assert.match(worker, pattern, `${name} route must be return-awaited inside the top-level try/catch`);
  assert.doesNotMatch(worker, new RegExp(`return ${name}\\(`), `${name} must not be bare-returned from the Worker route boundary`);
}

assert.match(worker, /try \{\s*await ensureSchema\(env\);[\s\S]*?return await createProfile[\s\S]*?return await startRun[\s\S]*?return await forwardSubmission[\s\S]*?return await leaderboard[\s\S]*?return await replayResponse[\s\S]*?\} catch \(err\) \{\s*console\.error\('VOIDCUT leaderboard error', err\);\s*return error\(request, 500, 'server-error', 'Leaderboard service error\.'\);/,
  'all async route dispatch must stay inside the controlled fetch try/catch');

// Demonstrate the rejection-containment semantic this source contract protects.
async function caughtWithAwait(handler) {
  try {
    return await handler();
  } catch {
    return 'caught';
  }
}
async function escapesWithoutAwait(handler) {
  try {
    return handler();
  } catch {
    return 'caught';
  }
}
const rejecting = async () => { throw new Error('route-failure'); };
assert.equal(await caughtWithAwait(rejecting), 'caught', 'return await keeps async rejection inside catch');
await assert.rejects(() => escapesWithoutAwait(rejecting), /route-failure/, 'bare return lets async rejection escape catch');

// F12 scheduled maintenance already has its own awaited error boundary.
assert.match(worker, /async scheduled\(controller, env\) \{\s*try \{\s*await ensureSchema\(env\);\s*const result = await runLeaderboardMaintenance\(/,
  'scheduled maintenance must retain its awaited try/catch boundary');

console.log('F13 Worker async route error-boundary regression PASS');
