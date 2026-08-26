import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.cwd(), '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const client = fs.readFileSync(path.join(root, 'leaderboard/client/global-leaderboard-runtime.js'), 'utf8');

for (const source of [html, client]) {
  assert.ok(source.includes("const LEADERBOARD_IDENTITY_KEY='voidcut.leaderboard.identity.v1';"), 'compatible primary identity key missing');
  assert.ok(source.includes("const LEADERBOARD_IDENTITY_BACKUP_KEY='voidcut.leaderboard.identity.backup.v1';"), 'identity backup key missing');
  assert.ok(source.includes("const LEADERBOARD_IDENTITY_TEST_KEY='voidcut.leaderboard.identity.storage-test.v1';"), 'identity storage-test key missing');
  for (const fn of [
    'normalizeLeaderboardIdentity',
    'leaderboardIdentityHash',
    'leaderboardIdentityEnvelope',
    'parseLeaderboardIdentitySnapshot',
    'leaderboardIdentityStorageSelfTest',
    'sameLeaderboardIdentity',
    'writeLeaderboardIdentityCopy',
    'repairLeaderboardIdentityCopies',
    'readStoredLeaderboardIdentity',
    'loadLeaderboardIdentity',
    'storeLeaderboardIdentity',
    'clearLeaderboardIdentity',
  ]) assert.ok(source.includes(`function ${fn}`), `missing F10 identity function: ${fn}`);
}

const helperMatch = client.match(/function normalizeLeaderboardIdentity\(x\)\{[\s\S]*?function clearLeaderboardIdentity\(\)\{[^\n]+\}/);
assert.ok(helperMatch, 'identity durability helper block missing');
assert.ok(html.includes(helperMatch[0]), 'source client and shipped inline identity helper block must match exactly');

class MemoryStorage {
  constructor() { this.map = new Map(); this.failWrites = false; this.failKeys = new Set(); }
  getItem(k) { return this.map.has(k) ? this.map.get(k) : null; }
  setItem(k, v) {
    if (this.failWrites || this.failKeys.has(k)) throw new Error('quota');
    this.map.set(k, String(v));
  }
  removeItem(k) { this.map.delete(k); }
}

function makeHelpers(storage) {
  return new Function(
    'localStorage',
    `const LEADERBOARD_IDENTITY_KEY='voidcut.leaderboard.identity.v1';
     const LEADERBOARD_IDENTITY_BACKUP_KEY='voidcut.leaderboard.identity.backup.v1';
     const LEADERBOARD_IDENTITY_TEST_KEY='voidcut.leaderboard.identity.storage-test.v1';
     let leaderboardIdentityMemory=null;
     ${helperMatch[0]}
     return {
       normalizeLeaderboardIdentity,
       leaderboardIdentityHash,
       leaderboardIdentityEnvelope,
       parseLeaderboardIdentitySnapshot,
       leaderboardIdentityStorageSelfTest,
       sameLeaderboardIdentity,
       repairLeaderboardIdentityCopies,
       readStoredLeaderboardIdentity,
       loadLeaderboardIdentity,
       storeLeaderboardIdentity,
       clearLeaderboardIdentity,
       getMemory:()=>leaderboardIdentityMemory,
       setMemory:x=>{leaderboardIdentityMemory=x},
     };`,
  )(storage);
}

const IDENT = { playerId: '12345678-abcd-1234-abcd-123456789abc', name: 'PLAYER ONE', token: 'token-value-1234567890-abcdef' };
const PRIMARY = 'voidcut.leaderboard.identity.v1';
const BACKUP = 'voidcut.leaderboard.identity.backup.v1';
const TEST = 'voidcut.leaderboard.identity.storage-test.v1';

{
  const storage = new MemoryStorage();
  const h = makeHelpers(storage);
  assert.deepEqual(h.normalizeLeaderboardIdentity({ ...IDENT, name: '  PLAYER   ONE  ' }), IDENT, 'identity normalization must canonicalize name whitespace');
  assert.equal(h.normalizeLeaderboardIdentity({ ...IDENT, name: 'x' }), null, 'invalid public name must be rejected');
  assert.equal(h.normalizeLeaderboardIdentity({ ...IDENT, token: 'short' }), null, 'implausibly short token must be rejected');
  assert.equal(h.storeLeaderboardIdentity(IDENT), true, 'valid identity must persist redundantly');
  assert.ok(storage.getItem(PRIMARY), 'primary identity snapshot missing');
  assert.ok(storage.getItem(BACKUP), 'backup identity snapshot missing');
  assert.deepEqual(h.parseLeaderboardIdentitySnapshot(storage.getItem(PRIMARY)).data, IDENT, 'primary readback mismatch');
  assert.deepEqual(h.parseLeaderboardIdentitySnapshot(storage.getItem(BACKUP)).data, IDENT, 'backup readback mismatch');
  assert.equal(storage.getItem(TEST), null, 'storage-test residue must be removed');
}

{
  const storage = new MemoryStorage();
  storage.setItem(PRIMARY, JSON.stringify(IDENT));
  const h = makeHelpers(storage);
  assert.deepEqual(h.loadLeaderboardIdentity(), IDENT, 'legacy raw identity must load');
  assert.equal(h.parseLeaderboardIdentitySnapshot(storage.getItem(PRIMARY)).legacy, false, 'legacy primary must be repaired into envelope');
  assert.equal(h.parseLeaderboardIdentitySnapshot(storage.getItem(BACKUP)).legacy, false, 'legacy identity must create backup envelope');
}

{
  const storage = new MemoryStorage();
  const h = makeHelpers(storage);
  assert.equal(h.storeLeaderboardIdentity(IDENT), true);
  storage.setItem(PRIMARY, '{corrupt');
  assert.deepEqual(h.loadLeaderboardIdentity(), IDENT, 'valid backup must recover corrupt primary');
  assert.deepEqual(h.parseLeaderboardIdentitySnapshot(storage.getItem(PRIMARY)).data, IDENT, 'recovery must repair primary');
  storage.setItem(BACKUP, '{corrupt');
  assert.deepEqual(h.loadLeaderboardIdentity(), IDENT, 'valid primary must recover corrupt backup');
  assert.deepEqual(h.parseLeaderboardIdentitySnapshot(storage.getItem(BACKUP)).data, IDENT, 'recovery must repair backup');
}

{
  const storage = new MemoryStorage();
  storage.setItem(PRIMARY, '{bad');
  storage.setItem(BACKUP, '{also-bad');
  const h = makeHelpers(storage);
  assert.equal(h.loadLeaderboardIdentity(), null, 'two invalid copies must not create an identity');
}

{
  const storage = new MemoryStorage();
  const h = makeHelpers(storage);
  assert.equal(h.storeLeaderboardIdentity(IDENT), true);
  h.clearLeaderboardIdentity();
  assert.equal(storage.getItem(PRIMARY), null, 'clear must remove primary identity');
  assert.equal(storage.getItem(BACKUP), null, 'clear must remove backup identity');
  assert.equal(storage.getItem(TEST), null, 'clear must remove test residue');
  assert.equal(h.getMemory(), null, 'clear must remove emergency in-memory identity');
}

{
  const storage = new MemoryStorage();
  const h = makeHelpers(storage);
  storage.failWrites = true;
  assert.equal(h.leaderboardIdentityStorageSelfTest(), false, 'storage self-test must fail closed');
  assert.equal(h.storeLeaderboardIdentity(IDENT), false, 'identity store must report unavailable storage');
  assert.deepEqual(h.getMemory(), IDENT, 'post-create emergency identity must remain available in memory');
}

const profile = client.match(/async function createLeaderboardProfileFromCard\(\)\{[^\n]+\}/)?.[0] || '';
assert.ok(profile, 'profile creation function missing');
const preflightAt = profile.indexOf('leaderboardIdentityStorageSelfTest()');
const requestAt = profile.indexOf("leaderboardRequest('/profile/create'");
assert.ok(preflightAt >= 0 && requestAt > preflightAt, 'identity storage preflight must occur before server profile creation');
assert.ok(profile.includes("status.textContent='LOCAL STORAGE UNAVAILABLE • PROFILE NOT CREATED';return"), 'preflight failure must stop profile creation explicitly');
assert.ok(profile.includes('if(!storeLeaderboardIdentity(ident))'), 'server-returned identity must require durable store success');
assert.ok(profile.includes("'PROFILE CREATED • IDENTITY STORAGE FAILED • EXPORT SAVE BEFORE CLOSING'"), 'post-create storage failure must surface recovery instruction');
assert.ok(profile.indexOf('if(!storeLeaderboardIdentity(ident))') < profile.indexOf('await drainLeaderboardSubmissionQueue()'), 'queued submissions must not drain before durable identity ownership');

assert.ok(client.includes("if(err?.status===401){clearLeaderboardIdentity();"), '401 recovery must clear hardened identity storage');
assert.ok(client.includes('const ident=useAuth?loadLeaderboardIdentity():null'), 'authenticated requests must use durable identity loader');
assert.ok(!client.includes('loadLeaderboardIdentity()||leaderboardIdentityMemory'), 'network auth must not silently use emergency-only identity memory');

const exportFn = html.match(/function exportFullSave\(\)\{[^\n]+\}/)?.[0] || '';
const importFn = html.match(/function importFullSave\(code\)\{[^\n]+\}/)?.[0] || '';
assert.ok(exportFn.includes('env={f:3,v:SAVE_SCHEMA'), 'full-save export must use credential-aware f:3 envelope');
assert.ok(exportFn.includes('identity=normalizeLeaderboardIdentity(loadLeaderboardIdentity()||leaderboardIdentityMemory)'), 'full-save export must include durable or emergency ownership credential');
assert.ok(exportFn.includes('payload={d:data,i:identity}'), 'f:3 package must contain save data and optional identity');
assert.ok(exportFn.includes('saveHash(JSON.stringify(payload))'), 'f:3 checksum must cover the full credential-bearing package');
assert.ok(importFn.includes('[1,2,3].includes(env?.f)'), 'full-save import must preserve f:1/f:2 compatibility and accept f:3');
assert.ok(importFn.includes("if(env.f===3)"), 'f:3 import branch missing');
assert.ok(importFn.includes('JSON.stringify({d:env.d,i:identity})'), 'f:3 import checksum must include identity');
assert.ok(importFn.includes('if(identity&&!storeLeaderboardIdentity(identity))leaderboardIdentityMemory=identity'), 'valid imported ownership must use durable restore with emergency fallback');

function hash(text) {
  let v = 2166136261 >>> 0;
  for (let i = 0; i < text.length; i++) { v ^= text.charCodeAt(i); v = Math.imul(v, 16777619) >>> 0; }
  return v.toString(16).padStart(8, '0').toUpperCase();
}
const saveData = { schemaVersion: 17, bestScore: 10 };
const pkg = { d: saveData, i: IDENT };
const goodHash = hash(JSON.stringify(pkg));
assert.notEqual(goodHash, hash(JSON.stringify({ d: saveData, i: { ...IDENT, token: IDENT.token + 'x' } })), 'identity tampering must change f:3 package checksum');
assert.notEqual(goodHash, hash(JSON.stringify({ d: { ...saveData, bestScore: 11 }, i: IDENT })), 'save tampering must change f:3 package checksum');

assert.ok(html.includes("const SAVE_SCHEMA=17,"), 'F10 must not bump gameplay save schema');
assert.ok(html.includes("const RELEASE_CONTRACT={save:17,replay:9,arena:2,director:6}"), 'F10 must not alter release gameplay/replay contracts');

console.log('F10 leaderboard identity durability regression PASS');
