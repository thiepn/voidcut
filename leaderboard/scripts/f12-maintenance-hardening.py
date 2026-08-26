from pathlib import Path

root = Path(__file__).resolve().parents[2]
worker = root / 'leaderboard' / 'src' / 'index.js'
wrangler = root / 'leaderboard' / 'wrangler.jsonc'
register = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

w = worker.read_text(encoding='utf-8')
w = replace_once(
    w,
    "const TICKET_TTL_MS = 6 * 60 * 60 * 1000;\n",
    "const TICKET_TTL_MS = 6 * 60 * 60 * 1000;\nconst TICKET_RETENTION_MS = 7 * 24 * 60 * 60 * 1000;\nconst TICKET_CLEANUP_BATCH = 500;\nconst REPLAY_GC_GRACE_MS = 24 * 60 * 60 * 1000;\nconst REPLAY_GC_BATCH = 50;\n",
    'maintenance constants',
)

old_schema_tail = """      env.DB.prepare('CREATE INDEX IF NOT EXISTS run_tickets_expiry_idx ON run_tickets(expires_at)'),
    ]).catch(err => {
"""
new_schema_tail = """      env.DB.prepare('CREATE INDEX IF NOT EXISTS run_tickets_expiry_idx ON run_tickets(expires_at)'),
      env.DB.prepare('CREATE INDEX IF NOT EXISTS run_tickets_used_idx ON run_tickets(used_at)'),
      env.DB.prepare(`CREATE TABLE IF NOT EXISTS replay_gc_queue (
        hash TEXT PRIMARY KEY,
        queued_at INTEGER NOT NULL
      )`),
      env.DB.prepare('CREATE INDEX IF NOT EXISTS replay_gc_queue_age_idx ON replay_gc_queue(queued_at)'),
      env.DB.prepare(`CREATE TRIGGER IF NOT EXISTS players_queue_displaced_replay
        AFTER UPDATE OF best_replay_hash ON players
        WHEN OLD.best_replay_hash IS NOT NULL AND OLD.best_replay_hash <> NEW.best_replay_hash
        BEGIN
          INSERT INTO replay_gc_queue(hash,queued_at) VALUES(OLD.best_replay_hash,NEW.updated_at)
          ON CONFLICT(hash) DO UPDATE SET queued_at=excluded.queued_at;
        END`),
    ]).catch(err => {
"""
w = replace_once(w, old_schema_tail, new_schema_tail, 'maintenance schema')

insert_after_snapshot = """async function playerSnapshot(env, id) {
  if (!id) return null;
  return env.DB.prepare('SELECT id,name,best_score,best_chamber,best_time,best_grade,best_replay_hash,updated_at FROM players WHERE id=? LIMIT 1').bind(id).first();
}
"""
maintenance_helpers = r"""
async function queueReplayForGc(env, hash, queuedAt = Date.now()) {
  const replayHash = normalizeReplayHash(hash);
  if (!replayHash) return false;
  await env.DB.prepare(`INSERT INTO replay_gc_queue(hash,queued_at) VALUES(?,?)
    ON CONFLICT(hash) DO UPDATE SET queued_at=excluded.queued_at`).bind(replayHash, Math.max(1, Math.floor(Number(queuedAt) || Date.now()))).run();
  return true;
}
async function cleanupRunTickets(env, now = Date.now()) {
  const cutoff = Math.max(0, Math.floor(Number(now) || Date.now()) - TICKET_RETENTION_MS);
  const used = await env.DB.prepare(`DELETE FROM run_tickets WHERE id IN (
    SELECT id FROM run_tickets WHERE used_at IS NOT NULL AND used_at < ? ORDER BY used_at ASC LIMIT ?
  )`).bind(cutoff, TICKET_CLEANUP_BATCH).run();
  const abandoned = await env.DB.prepare(`DELETE FROM run_tickets WHERE id IN (
    SELECT id FROM run_tickets WHERE used_at IS NULL AND expires_at < ? ORDER BY expires_at ASC LIMIT ?
  )`).bind(cutoff, TICKET_CLEANUP_BATCH).run();
  return Number(used?.meta?.changes || 0) + Number(abandoned?.meta?.changes || 0);
}
async function cleanupReplayGc(env, now = Date.now()) {
  const cutoff = Math.max(0, Math.floor(Number(now) || Date.now()) - REPLAY_GC_GRACE_MS);
  const pending = await env.DB.prepare(`SELECT hash,queued_at FROM replay_gc_queue WHERE queued_at < ? ORDER BY queued_at ASC LIMIT ?`).bind(cutoff, REPLAY_GC_BATCH).all();
  let deleted = 0, released = 0;
  for (const row of pending.results || []) {
    const replayHash = normalizeReplayHash(row?.hash), queuedAt = Number(row?.queued_at);
    if (!replayHash || !Number.isFinite(queuedAt)) {
      if (row?.hash != null) await env.DB.prepare('DELETE FROM replay_gc_queue WHERE hash=?').bind(String(row.hash)).run();
      continue;
    }
    const current = await env.DB.prepare('SELECT queued_at FROM replay_gc_queue WHERE hash=? LIMIT 1').bind(replayHash).first();
    if (Number(current?.queued_at) !== queuedAt) continue;
    const owner = await env.DB.prepare('SELECT id FROM players WHERE best_replay_hash=? LIMIT 1').bind(replayHash).first();
    if (owner) {
      const drop = await env.DB.prepare('DELETE FROM replay_gc_queue WHERE hash=? AND queued_at=?').bind(replayHash, queuedAt).run();
      released += Number(drop?.meta?.changes || 0);
      continue;
    }
    await env.REPLAYS.delete(`verified/${replayHash}.json`);
    const drop = await env.DB.prepare(`DELETE FROM replay_gc_queue WHERE hash=? AND queued_at=?
      AND NOT EXISTS (SELECT 1 FROM players WHERE best_replay_hash=?)`).bind(replayHash, queuedAt, replayHash).run();
    deleted += Number(drop?.meta?.changes || 0);
  }
  return { deleted, released };
}
async function runLeaderboardMaintenance(env, now = Date.now()) {
  const ticketsDeleted = await cleanupRunTickets(env, now);
  const replayGc = await cleanupReplayGc(env, now);
  return { ticketsDeleted, replayGc };
}
"""
w = replace_once(w, insert_after_snapshot, insert_after_snapshot + maintenance_helpers, 'maintenance helpers')

old_put = """    if (better) {
      await this.env.REPLAYS.put(`verified/${serverReplayHash}.json`, JSON.stringify(replay), { httpMetadata: { contentType: 'application/json' } });
      const update = await this.env.DB.prepare(`UPDATE players SET best_score=?,best_chamber=?,best_time=?,best_grade=?,best_replay_hash=?,updated_at=?
"""
new_put = """    if (better) {
      await queueReplayForGc(this.env, serverReplayHash, now);
      await this.env.REPLAYS.put(`verified/${serverReplayHash}.json`, JSON.stringify(replay), { httpMetadata: { contentType: 'application/json' } });
      const update = await this.env.DB.prepare(`UPDATE players SET best_score=?,best_chamber=?,best_time=?,best_grade=?,best_replay_hash=?,updated_at=?
"""
w = replace_once(w, old_put, new_put, 'pre-upload replay gc registration')

old_delete = """      personalBest = Number(update?.meta?.changes || 0) > 0;
      if (!personalBest) await this.env.REPLAYS.delete(`verified/${serverReplayHash}.json`);
      else if (old?.best_replay_hash && old.best_replay_hash !== serverReplayHash) this.ctx.waitUntil((async()=>{const refs=await this.env.DB.prepare('SELECT COUNT(*) AS n FROM players WHERE best_replay_hash=?').bind(old.best_replay_hash).first('n');if(Number(refs||0)===0)await this.env.REPLAYS.delete(`verified/${old.best_replay_hash}.json`)})());
"""
new_delete = """      personalBest = Number(update?.meta?.changes || 0) > 0;
"""
w = replace_once(w, old_delete, new_delete, 'remove snapshot-based R2 deletion')

old_default_end = """    } catch (err) {
      console.error('VOIDCUT leaderboard error', err);
      return error(request, 500, 'server-error', 'Leaderboard service error.');
    }
  },
};
"""
new_default_end = """    } catch (err) {
      console.error('VOIDCUT leaderboard error', err);
      return error(request, 500, 'server-error', 'Leaderboard service error.');
    }
  },
  async scheduled(controller, env) {
    try {
      await ensureSchema(env);
      const result = await runLeaderboardMaintenance(env, Number(controller?.scheduledTime) || Date.now());
      console.log('VOIDCUT leaderboard maintenance', result);
    } catch (err) {
      console.error('VOIDCUT leaderboard maintenance error', err);
      throw err;
    }
  },
};
"""
w = replace_once(w, old_default_end, new_default_end, 'scheduled maintenance handler')
worker.write_text(w, encoding='utf-8')

cfg = wrangler.read_text(encoding='utf-8')
cfg = replace_once(
    cfg,
    '  "workers_dev": true,\n',
    '  "workers_dev": true,\n  "triggers": { "crons": ["*/15 * * * *"] },\n',
    'cron trigger',
)
wrangler.write_text(cfg, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old_013 = '| VC-013 | MEDIUM | Expired/rejected/used run tickets have no retention cleanup and accumulate indefinitely. | F12 | OPEN |'
new_013 = '| VC-013 | MEDIUM | Expired/rejected/used run tickets have no retention cleanup and accumulate indefinitely. | F12 | FIXED — VERIFYING |'
old_014 = '| VC-014 | LOW | Concurrent personal-best updates can leave obsolete/orphaned R2 replay objects. | F12 | OPEN |'
new_014 = '| VC-014 | LOW | Concurrent personal-best updates can leave obsolete/orphaned R2 replay objects. | F12 | FIXED — VERIFYING |'
if r.count(old_013) != 1 or r.count(old_014) != 1:
    raise SystemExit('F12 register markers missing')
r = r.replace(old_013, new_013, 1).replace(old_014, new_014, 1)
r += '''\n## F12 implementation record — ticket retention and replay-object garbage collection\n\n- Run tickets now have a seven-day retention window after terminal use or abandoned expiry. A scheduled maintenance pass deletes at most 500 old used tickets and 500 old never-used expired tickets per run, preventing unbounded D1 growth while preserving a generous retry/audit window.\n- `run_tickets.used_at` now has a dedicated cleanup index in addition to the existing expiry index.\n- The Worker now owns a D1 `replay_gc_queue` and a `players_queue_displaced_replay` SQLite trigger. Whenever a player's `best_replay_hash` actually changes, the trigger records the database row's true OLD replay hash, not the potentially stale JavaScript snapshot read before a concurrent PB update.\n- Every candidate replay that is about to be written to R2 is queued for garbage collection before the upload. This covers failed conditional PB updates and failures after an R2 write without immediately deleting an object that another profile could reference.\n- The old snapshot-based `old.best_replay_hash` background deletion and unconditional failed-PB candidate deletion have been removed. Those paths could miss an intermediate concurrent winner or delete a content-addressed object still referenced elsewhere.\n- Replay GC waits 24 hours, processes at most 50 candidates per scheduled run, re-checks the queue generation and live `players.best_replay_hash` references before deletion, deletes only unreferenced `verified/<sha256>.json` objects, and drops queue entries that remain legitimately referenced. A future displacement re-queues the hash transactionally through the trigger.\n- Wrangler now configures `*/15 * * * *` as the maintenance Cron Trigger, and the Worker exports a matching `scheduled()` handler.\n- No ticket TTL, replay format, verification rules, scoring, ranking, client queue, save schema, gameplay, or UI behavior changed in F12.\n'''
register.write_text(r, encoding='utf-8')
