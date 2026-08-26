import fs from 'node:fs';
import assert from 'node:assert/strict';

const root = new URL('../../', import.meta.url);
const index = fs.readFileSync(new URL('index.html', root), 'utf8');
const worker = fs.readFileSync(new URL('leaderboard/src/index.js', root), 'utf8');

function extractOneLineFunction(source, name) {
  const re = new RegExp(`function ${name}\\([^\\n]+`);
  const match = source.match(re);
  assert.ok(match, `${name} must exist`);
  return match[0];
}

const indexComparatorSource = extractOneLineFunction(index, 'compareLeaderboardRank');
const workerComparatorSource = extractOneLineFunction(worker, 'compareLeaderboardRank');
assert.equal(workerComparatorSource, indexComparatorSource, 'browser and Worker must share the exact canonical ranking comparator');

const compareLeaderboardRank = new Function(`${indexComparatorSource}; return compareLeaderboardRank;`)();
const cmp = (a, b) => Math.sign(compareLeaderboardRank(a, b));

assert.equal(cmp({score:101,chamber:2,time:20},{score:100,chamber:99,time:1}), -1, 'higher score ranks first');
assert.equal(cmp({score:100,chamber:3,time:50},{score:100,chamber:2,time:1}), -1, 'deeper chamber breaks score ties');
assert.equal(cmp({score:100,chamber:3,time:40},{score:100,chamber:3,time:41}), -1, 'faster time breaks score/chamber ties');
assert.equal(cmp({score:100,chamber:3,time:40,updatedAt:10},{score:100,chamber:3,time:40,updatedAt:11}), -1, 'earlier update timestamp breaks result ties');
assert.equal(cmp({score:100,chamber:3,time:40,updatedAt:10,id:'a'},{score:100,chamber:3,time:40,updatedAt:10,id:'b'}), -1, 'lexicographically smaller stable id is the final tie-break');
assert.equal(cmp({score:100,chamber:3,time:null},{score:100,chamber:3,time:40}), 1, 'missing time sorts after finite time');
assert.equal(cmp({score:100,chamber:3,time:40,updatedAt:10,id:'same'},{score:100,chamber:3,time:40,updatedAt:10,id:'same'}), 0, 'identical canonical entries compare equal');

assert.match(index, /function replayLeaderboardRankEntry\(r,updatedAt,id\)\{return\{score:r\?\.score,chamber:r\?\.chamber,time:r\?\.deathTime,updatedAt,id\}\}/, 'local replay values must map to the canonical ranking fields');
assert.match(index, /function rankCompetitiveRuns\(entries\).*?\.sort\(\(a,b\)=>compareLeaderboardRank\(replayLeaderboardRankEntry\(a\.replay,a\.recordedAt,a\.replay\.hash\),replayLeaderboardRankEntry\(b\.replay,b\.recordedAt,b\.replay\.hash\)\)\)/s, 'local top runs must use the canonical comparator');
assert.doesNotMatch(index, /b\.replay\.score-a\.replay\.score\|\|b\.replay\.chamber-a\.replay\.chamber/, 'old ad-hoc local comparator must be removed');
assert.match(index, /!validReplay\(save\.bestReplay\)\|\|compareLeaderboardRank\(replayLeaderboardRankEntry\(completed\),replayLeaderboardRankEntry\(save\.bestReplay\)\)<0/, 'best replay selection must use canonical score/chamber/time ordering');
assert.doesNotMatch(index, /completed\.score>save\.bestReplay\.score/, 'score-only best replay replacement must be removed');

assert.match(worker, /ORDER BY best_score DESC,best_chamber DESC,COALESCE\(best_time,1e99\) ASC,updated_at ASC,id ASC LIMIT \?/, 'D1 LIMIT ordering must match the canonical five-field order');
assert.match(worker, /best_replay_hash AS replayHash,updated_at AS updatedAt/, 'global rows need the canonical timestamp field for comparator sorting');
assert.match(worker, /const ordered = \(result\.results \|\| \[\]\)\.sort\(compareLeaderboardRank\);/, 'global returned rows must pass through the canonical comparator');
assert.match(worker, /ordered\.map\(\(\{ updatedAt, \.\.\.r \}, i\) => \(\{ rank: i \+ 1, \.\.\.r \}\)\)/, 'internal timestamp must not leak into public leaderboard rows');
assert.match(worker, /updated_at = \? AND id < \?/, 'self rank must include the final id ASC tie-break');
assert.match(worker, /\.bind\(score, score, chamber, score, chamber, time, score, chamber, time, updatedAt, score, chamber, time, updatedAt, id\)/, 'self-rank bind list must supply the exact-tie id predicate');
assert.match(worker, /const better = !old \|\| compareLeaderboardRank\(/, 'Worker personal-best precheck must use the canonical comparator');
assert.doesNotMatch(worker, /official\.score > Number\(old\.best_score/, 'old ad-hoc Worker personal-best comparison must be removed');

const tied = [
  {score:500,chamber:8,time:30,updatedAt:100,id:'0002'},
  {score:500,chamber:8,time:30,updatedAt:100,id:'0001'},
  {score:500,chamber:8,time:29,updatedAt:999,id:'9999'},
];
const ordered = [...tied].sort(compareLeaderboardRank);
assert.deepEqual(ordered.map(x=>x.id), ['9999','0001','0002'], 'time precedes timestamp/id, and id resolves an otherwise exact tie');
const target = tied[0];
const expectedRank = tied.filter(x => compareLeaderboardRank(x, target) < 0).length + 1;
assert.equal(expectedRank, 3, 'exact-tie self rank must count the lexicographically smaller id ahead of the target');

console.log('F11 leaderboard ranking consistency PASS');
