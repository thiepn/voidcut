from pathlib import Path

root = Path(__file__).resolve().parents[2]
index = root / 'index.html'
worker = root / 'leaderboard' / 'src' / 'index.js'
register = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)


comparator = """function compareLeaderboardRank(a,b){const scoreA=Number.isFinite(Number(a?.score))?Number(a.score):0,scoreB=Number.isFinite(Number(b?.score))?Number(b.score):0;if(scoreA!==scoreB)return scoreA>scoreB?-1:1;const chamberA=Number.isFinite(Number(a?.chamber))?Number(a.chamber):1,chamberB=Number.isFinite(Number(b?.chamber))?Number(b.chamber):1;if(chamberA!==chamberB)return chamberA>chamberB?-1:1;const timeA=Number.isFinite(Number(a?.time))?Number(a.time):Infinity,timeB=Number.isFinite(Number(b?.time))?Number(b.time):Infinity;if(timeA!==timeB)return timeA<timeB?-1:1;const updatedA=Number.isFinite(Number(a?.updatedAt))?Number(a.updatedAt):Infinity,updatedB=Number.isFinite(Number(b?.updatedAt))?Number(b.updatedAt):Infinity;if(updatedA!==updatedB)return updatedA<updatedB?-1:1;const idA=String(a?.id??''),idB=String(b?.id??'');if(idA!==idB)return idA<idB?-1:1;return 0}
"""

old_local = "function rankCompetitiveRuns(entries){const unique=new Map;for(const e of entries||[]){if(!e||!verifyCompetitiveReplay(e.replay))continue;const old=unique.get(e.replay.hash);if(!old||e.recordedAt<old.recordedAt)unique.set(e.replay.hash,e)}return[...unique.values()].sort((a,b)=>b.replay.score-a.replay.score||b.replay.chamber-a.replay.chamber||a.replay.deathTime-b.replay.deathTime||a.recordedAt-b.recordedAt||a.replay.hash.localeCompare(b.replay.hash)).slice(0,10)}"
new_local = comparator + "function replayLeaderboardRankEntry(r,updatedAt,id){return{score:r?.score,chamber:r?.chamber,time:r?.deathTime,updatedAt,id}}\nfunction rankCompetitiveRuns(entries){const unique=new Map;for(const e of entries||[]){if(!e||!verifyCompetitiveReplay(e.replay))continue;const old=unique.get(e.replay.hash);if(!old||e.recordedAt<old.recordedAt)unique.set(e.replay.hash,e)}return[...unique.values()].sort((a,b)=>compareLeaderboardRank(replayLeaderboardRankEntry(a.replay,a.recordedAt,a.replay.hash),replayLeaderboardRankEntry(b.replay,b.recordedAt,b.replay.hash))).slice(0,10)}"

old_best = "if(completed&&(!validReplay(save.bestReplay)||completed.score>save.bestReplay.score)){save.bestReplay=completed;if(!best)newRecords.push('BEST REPLAY')}"
new_best = "if(completed&&(!validReplay(save.bestReplay)||compareLeaderboardRank(replayLeaderboardRankEntry(completed),replayLeaderboardRankEntry(save.bestReplay))<0)){save.bestReplay=completed;if(!best)newRecords.push('BEST REPLAY')}"

s = index.read_text(encoding='utf-8')
s = replace_once(s, old_local, new_local, 'inline canonical ranking comparator')
s = replace_once(s, old_best, new_best, 'inline best replay comparator')
index.write_text(s, encoding='utf-8')

w = worker.read_text(encoding='utf-8')
insert_after = "function preauthKey(request) {\n  const ip = String(request.headers.get('CF-Connecting-IP') || '').trim();\n  return `ip:${ip || 'unknown'}`;\n}\n"
worker_comparator = comparator.replace(';const ', ';\n  const ').replace(';if(', ';\n  if(').replace(';return 0}', ';\n  return 0;\n}')
# Keep the exact compact comparator text in both browser and Worker so the contract can be source-compared.
w = replace_once(w, insert_after, insert_after + comparator, 'worker canonical comparator insertion')

old_rank = """async function rankForPlayer(env, player) {
  if (!player || !Number.isFinite(player.best_score) || player.best_score <= 0) return null;
  const rank = await env.DB.prepare(`SELECT COUNT(*) + 1 AS rank FROM players
    WHERE best_score > ?
       OR (best_score = ? AND best_chamber > ?)
       OR (best_score = ? AND best_chamber = ? AND COALESCE(best_time, 1e99) < COALESCE(?, 1e99))
       OR (best_score = ? AND best_chamber = ? AND COALESCE(best_time, 1e99) = COALESCE(?, 1e99) AND updated_at < ?)`)
    .bind(player.best_score, player.best_score, player.best_chamber, player.best_score, player.best_chamber, player.best_time, player.best_score, player.best_chamber, player.best_time, player.updated_at || 0)
    .first('rank');
  return Number(rank || 1);
}
"""
new_rank = """async function rankForPlayer(env, player) {
  if (!player || !Number.isFinite(player.best_score) || player.best_score <= 0) return null;
  const score=Number(player.best_score),chamber=Number(player.best_chamber||1),time=player.best_time,updatedAt=Number(player.updated_at||0),id=String(player.id||'');
  const rank = await env.DB.prepare(`SELECT COUNT(*) + 1 AS rank FROM players
    WHERE best_score > ?
       OR (best_score = ? AND best_chamber > ?)
       OR (best_score = ? AND best_chamber = ? AND COALESCE(best_time, 1e99) < COALESCE(?, 1e99))
       OR (best_score = ? AND best_chamber = ? AND COALESCE(best_time, 1e99) = COALESCE(?, 1e99) AND updated_at < ?)
       OR (best_score = ? AND best_chamber = ? AND COALESCE(best_time, 1e99) = COALESCE(?, 1e99) AND updated_at = ? AND id < ?)`)
    .bind(score, score, chamber, score, chamber, time, score, chamber, time, updatedAt, score, chamber, time, updatedAt, id)
    .first('rank');
  return Number(rank || 1);
}
"""
w = replace_once(w, old_rank, new_rank, 'self rank final id tie-break')

old_board = """  const result = await env.DB.prepare(`SELECT id,name,best_score AS score,best_chamber AS chamber,best_time AS time,best_grade AS grade,best_replay_hash AS replayHash
    FROM players WHERE best_score>0
    ORDER BY best_score DESC,best_chamber DESC,COALESCE(best_time,1e99) ASC,updated_at ASC,id ASC LIMIT ?`).bind(limit).all();
  const rows = (result.results || []).map((r, i) => ({ rank: i + 1, ...r }));
"""
new_board = """  const result = await env.DB.prepare(`SELECT id,name,best_score AS score,best_chamber AS chamber,best_time AS time,best_grade AS grade,best_replay_hash AS replayHash,updated_at AS updatedAt
    FROM players WHERE best_score>0
    ORDER BY best_score DESC,best_chamber DESC,COALESCE(best_time,1e99) ASC,updated_at ASC,id ASC LIMIT ?`).bind(limit).all();
  const ordered = (result.results || []).sort(compareLeaderboardRank);
  const rows = ordered.map(({ updatedAt, ...r }, i) => ({ rank: i + 1, ...r }));
"""
w = replace_once(w, old_board, new_board, 'global rows canonical comparator')

old_better = """    const better = !old || official.score > Number(old.best_score || 0)
      || (official.score === Number(old.best_score || 0) && official.chamber > Number(old.best_chamber || 1))
      || (official.score === Number(old.best_score || 0) && official.chamber === Number(old.best_chamber || 1) && (old.best_time == null || official.deathTime < Number(old.best_time)));
"""
new_better = """    const better = !old || compareLeaderboardRank(
      {score:official.score,chamber:official.chamber,time:official.deathTime},
      {score:old.best_score,chamber:old.best_chamber,time:old.best_time}
    ) < 0;
"""
w = replace_once(w, old_better, new_better, 'worker personal best canonical comparator')
worker.write_text(w, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old_011 = '| VC-011 | MEDIUM | Local best-replay selection does not use the same score/chamber/time ordering as the global leaderboard. | F11 | OPEN |'
new_011 = '| VC-011 | MEDIUM | Local best-replay selection does not use the same score/chamber/time ordering as the global leaderboard. | F11 | FIXED — VERIFYING |'
old_012 = '| VC-012 | LOW | Exact-tie self-rank calculation omits the final player-ID tie-break used by leaderboard ordering. | F11 | OPEN |'
new_012 = '| VC-012 | LOW | Exact-tie self-rank calculation omits the final player-ID tie-break used by leaderboard ordering. | F11 | FIXED — VERIFYING |'
if r.count(old_011) != 1 or r.count(old_012) != 1:
    raise SystemExit('F11 register markers missing')
r = r.replace(old_011, new_011, 1).replace(old_012, new_012, 1)
r += '''\n## F11 implementation record — canonical ranking and exact-tie self rank\n\n- A single canonical `compareLeaderboardRank` contract now defines ordering as score DESC, chamber DESC, time ASC, update/record timestamp ASC, stable ID ASC.\n- The exact comparator function text is mirrored in the shipped browser runtime and Worker and is regression-checked for identity, preventing silent semantic drift between local and server ranking logic.\n- Local competitive-run ranking maps `recordedAt` to the canonical timestamp field and replay hash to the canonical stable-ID field, preserving deterministic local ties while sharing the global score/chamber/time semantics.\n- `save.bestReplay` no longer compares score alone: equal-score deeper runs now replace shallower runs, and equal-score/equal-chamber faster runs replace slower runs. Exact score/chamber/time ties leave the existing best replay unchanged.\n- Worker personal-best prechecks now use the same canonical comparator for score/chamber/time before the existing conditional D1 update.\n- Global top-list rows include `updated_at` only internally, are re-sorted through the canonical comparator after the indexed SQL top-list query, then strip the internal timestamp before returning API rows.\n- The D1 top-list query remains ordered by score DESC, chamber DESC, null-safe time ASC, updated_at ASC, id ASC so LIMIT selection and the canonical comparator agree.\n- `rankForPlayer` now counts players with an equal score/chamber/time/update timestamp and lexicographically smaller player ID, matching the list's final `id ASC` tie-break.\n- No scoring, physics, replay, ticket, save-schema, identity, submission-queue or UI-design behavior changed in F11.\n'''
register.write_text(r, encoding='utf-8')
