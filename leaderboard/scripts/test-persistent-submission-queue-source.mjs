import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..');
const indexPath = path.join(root, 'index.html');
const clientPath = path.join(root, 'leaderboard/client/global-leaderboard-runtime.js');
const html = fs.readFileSync(indexPath, 'utf8');
const client = fs.readFileSync(clientPath, 'utf8');

for (const source of [html, client]) {
  assert.ok(source.includes("const LEADERBOARD_SUBMISSION_QUEUE_KEY='voidcut.leaderboard.submissions.v1';"), 'persistent queue key missing');
  assert.ok(source.includes('const LEADERBOARD_SUBMISSION_QUEUE_LIMIT=16;'), 'queue bound missing');
  assert.ok(source.includes('const LEADERBOARD_QUEUE_RETRY_MS=15000;'), 'retry bound missing');
  assert.ok(!source.includes('pendingLeaderboardSubmission'), 'obsolete single pending submission slot must be removed');
  assert.ok(!source.includes('submitLeaderboardRun('), 'obsolete direct single-run submit path must be removed');
  for (const fn of [
    'normalizeLeaderboardSubmissionQueue',
    'loadLeaderboardSubmissionQueue',
    'persistLeaderboardSubmissionQueue',
    'enqueueLeaderboardSubmission',
    'removeLeaderboardSubmission',
    'terminalLeaderboardSubmissionError',
    'scheduleLeaderboardQueueRetry',
    'submitLeaderboardQueueEntry',
    'drainLeaderboardSubmissionQueue',
    'queueLeaderboardSubmission',
  ]) assert.ok(source.includes(`function ${fn}`) || source.includes(`async function ${fn}`), `missing F9 function: ${fn}`);
}

const pureMatch = client.match(/function normalizeLeaderboardSubmissionQueue[\s\S]*?function terminalLeaderboardSubmissionError\(err\)\{[^\n]+\}/);
assert.ok(pureMatch, 'pure persistent queue helper block missing');

class MemoryStorage {
  constructor() { this.map = new Map(); this.failWrites = false; }
  getItem(k) { return this.map.has(k) ? this.map.get(k) : null; }
  setItem(k, v) { if (this.failWrites) throw new Error('quota'); this.map.set(k, String(v)); }
  removeItem(k) { this.map.delete(k); }
}

const storage = new MemoryStorage();
const helpers = new Function(
  'localStorage',
  `const LEADERBOARD_SUBMISSION_QUEUE_KEY='voidcut.leaderboard.submissions.v1';
   const LEADERBOARD_SUBMISSION_QUEUE_LIMIT=16;
   let leaderboardSubmissionQueue=[];
   let leaderboardQueueRetryTimer=null;
   ${pureMatch[0]}
   return {
     normalizeLeaderboardSubmissionQueue,
     loadLeaderboardSubmissionQueue,
     persistLeaderboardSubmissionQueue,
     enqueueLeaderboardSubmission,
     removeLeaderboardSubmission,
     terminalLeaderboardSubmissionError,
     getQueue:()=>leaderboardSubmissionQueue,
     setQueue:q=>{leaderboardSubmissionQueue=q},
   };`,
)(storage);

const future = Date.now() + 60_000;
const ticket = (id, seed = 1, expiresAt = future) => ({ ticketId: id, seed, expiresAt });
const replay = (seed = 1, score = 10) => ({ version: 9, arenaGeneration: 2, directorGeneration: 6, seed, events: [], score, chamber: 1, deathTime: 1, hash: 'a'.repeat(64) });

assert.deepEqual(helpers.loadLeaderboardSubmissionQueue(), [], 'empty storage must load as empty queue');
storage.setItem('voidcut.leaderboard.submissions.v1', '{broken');
assert.deepEqual(helpers.loadLeaderboardSubmissionQueue(), [], 'corrupt queue JSON must fail closed');
assert.equal(storage.getItem('voidcut.leaderboard.submissions.v1'), null, 'corrupt queue JSON should be cleared');

assert.equal(helpers.enqueueLeaderboardSubmission(replay(1, 10), ticket('ticket-1', 1)), 'queued');
assert.equal(helpers.enqueueLeaderboardSubmission(replay(2, 20), ticket('ticket-2', 2)), 'queued');
assert.equal(helpers.getQueue().length, 2, 'two submissions must coexist without overwrite');
let stored = JSON.parse(storage.getItem('voidcut.leaderboard.submissions.v1'));
assert.equal(stored.length, 2, 'both submissions must persist');
assert.deepEqual(stored.map(x => x.id), ['ticket-1', 'ticket-2']);

assert.equal(helpers.enqueueLeaderboardSubmission(replay(1, 99), ticket('ticket-1', 1)), 'queued');
assert.equal(helpers.getQueue().length, 2, 'duplicate ticket must replace, not duplicate');
assert.equal(helpers.getQueue().find(x => x.id === 'ticket-1').replay.score, 99, 'duplicate ticket should retain latest local payload');

helpers.setQueue([]);
const reloaded = helpers.loadLeaderboardSubmissionQueue();
assert.equal(reloaded.length, 2, 'persisted queue must survive a simulated reload');
assert.deepEqual(reloaded.map(x => x.id).sort(), ['ticket-1', 'ticket-2']);

const expiredRaw = [
  { id: 'expired', ticket: ticket('expired', 3, Date.now() - 1000), replay: replay(3), queuedAt: Date.now() - 5000 },
  { id: 'live', ticket: ticket('live', 4, future), replay: replay(4), queuedAt: Date.now() },
];
storage.setItem('voidcut.leaderboard.submissions.v1', JSON.stringify(expiredRaw));
const pruned = helpers.loadLeaderboardSubmissionQueue();
assert.deepEqual(pruned.map(x => x.id), ['live'], 'expired tickets must be pruned on load');

const full = Array.from({ length: 16 }, (_, i) => ({ id: `full-${i}`, ticket: ticket(`full-${i}`, i + 10), replay: replay(i + 10), queuedAt: Date.now() + i }));
helpers.setQueue(full);
assert.equal(helpers.persistLeaderboardSubmissionQueue(full), true, 'full bounded queue should persist');
assert.equal(helpers.enqueueLeaderboardSubmission(replay(99), ticket('overflow', 99)), 'full', 'queue must not evict an existing valid entry to admit overflow');
assert.equal(helpers.getQueue().length, 16, 'overflow attempt must preserve all existing entries');
assert.ok(!helpers.getQueue().some(x => x.id === 'overflow'));

storage.failWrites = true;
helpers.setQueue([]);
assert.equal(helpers.enqueueLeaderboardSubmission(replay(7), ticket('volatile', 7)), 'volatile', 'storage failure must be surfaced');
assert.equal(helpers.getQueue().length, 1, 'storage failure should retain current-session best-effort queue entry');
storage.failWrites = false;

for (const status of [400, 403, 404, 409, 410, 413, 422]) assert.equal(helpers.terminalLeaderboardSubmissionError({ status }), true, `status ${status} must be terminal`);
for (const status of [0, 401, 429, 500, 503]) assert.equal(helpers.terminalLeaderboardSubmissionError({ status }), false, `status ${status} must remain retryable/recoverable`);

const queueFn = client.match(/function queueLeaderboardSubmission\(replay,ticket\)\{[^\n]+\}/)?.[0] || '';
assert.ok(queueFn.includes('enqueueLeaderboardSubmission(replay,ticket)'), 'submission must enter queue before networking');
assert.ok(queueFn.indexOf('enqueueLeaderboardSubmission(replay,ticket)') < queueFn.indexOf('drainLeaderboardSubmissionQueue()'), 'queue persistence must precede drain');
assert.ok(queueFn.includes("result==='full'"), 'queue-full path must be explicit');
assert.ok(queueFn.includes("result==='volatile'"), 'storage-failure path must be explicit');

const drainFn = client.match(/async function drainLeaderboardSubmissionQueue\(\)\{[^\n]+\}/)?.[0] || '';
assert.ok(drainFn.includes('if(leaderboardQueueDrainPromise)return leaderboardQueueDrainPromise'), 'parallel drains must collapse to one promise');
assert.ok(drainFn.includes('while(leaderboardSubmissionQueue.length)'), 'drain must process multiple queued entries');
assert.ok(drainFn.includes('removeLeaderboardSubmission(entry.id)'), 'drain must remove entries individually');
assert.ok(drainFn.includes('terminalLeaderboardSubmissionError(err)'), 'terminal failures must be classified');
assert.ok(drainFn.includes('scheduleLeaderboardQueueRetry();break'), 'transient failure must retain queue and schedule retry');
assert.ok(drainFn.includes("if(err?.status===401){clearLeaderboardIdentity();"), '401 must preserve queue and recover identity');

assert.ok(client.includes('await drainLeaderboardSubmissionQueue()'), 'profile creation must drain the whole queue');
assert.ok(client.includes("window.addEventListener('online',()=>void drainLeaderboardSubmissionQueue());"), 'online recovery hook missing');
assert.ok(html.includes("void prefetchLeaderboardTicket();\nvoid drainLeaderboardSubmissionQueue();"), 'menu entry must resume persistent queue draining');
assert.ok(html.includes("leaderboardSubmissionQueue=loadLeaderboardSubmissionQueue();"), 'inline queue must restore from persistent storage on load');
assert.ok(client.includes("leaderboardSubmissionQueue=loadLeaderboardSubmissionQueue();"), 'source client queue must restore from persistent storage on load');

console.log('F9 persistent multi-entry submission queue regression PASS');
