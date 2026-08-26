from pathlib import Path
import json, re, sqlite3

root = Path(__file__).resolve().parents[2]
worker = (root / 'leaderboard' / 'src' / 'index.js').read_text(encoding='utf-8')
wrangler = (root / 'leaderboard' / 'wrangler.jsonc').read_text(encoding='utf-8')

assert 'const TICKET_RETENTION_MS = 7 * 24 * 60 * 60 * 1000;' in worker
assert 'const TICKET_CLEANUP_BATCH = 500;' in worker
assert 'const REPLAY_GC_GRACE_MS = 24 * 60 * 60 * 1000;' in worker
assert 'const REPLAY_GC_BATCH = 50;' in worker
assert 'CREATE INDEX IF NOT EXISTS run_tickets_used_idx ON run_tickets(used_at)' in worker
assert 'CREATE TABLE IF NOT EXISTS replay_gc_queue' in worker
assert 'CREATE INDEX IF NOT EXISTS replay_gc_queue_age_idx ON replay_gc_queue(queued_at)' in worker
assert 'CREATE TRIGGER IF NOT EXISTS players_queue_displaced_replay' in worker
assert 'OLD.best_replay_hash IS NOT NULL AND OLD.best_replay_hash <> NEW.best_replay_hash' in worker
assert 'VALUES(OLD.best_replay_hash,NEW.updated_at)' in worker
assert 'ON CONFLICT(hash) DO UPDATE SET queued_at=excluded.queued_at' in worker
assert 'SELECT id FROM run_tickets WHERE used_at IS NOT NULL AND used_at < ? ORDER BY used_at ASC LIMIT ?' in worker
assert 'SELECT id FROM run_tickets WHERE used_at IS NULL AND expires_at < ? ORDER BY expires_at ASC LIMIT ?' in worker
assert 'await queueReplayForGc(this.env, serverReplayHash, now);' in worker
assert worker.index('await queueReplayForGc(this.env, serverReplayHash, now);') < worker.index('await this.env.REPLAYS.put(`verified/${serverReplayHash}.json`')
assert "if (!personalBest) await this.env.REPLAYS.delete" not in worker
assert 'old?.best_replay_hash' not in worker
assert 'SELECT hash,queued_at FROM replay_gc_queue WHERE queued_at < ? ORDER BY queued_at ASC LIMIT ?' in worker
assert "SELECT id FROM players WHERE best_replay_hash=? LIMIT 1" in worker
assert "await env.REPLAYS.delete(`verified/${replayHash}.json`);" in worker
assert 'AND NOT EXISTS (SELECT 1 FROM players WHERE best_replay_hash=?)' in worker
assert 'async scheduled(controller, env)' in worker
assert 'runLeaderboardMaintenance(env, Number(controller?.scheduledTime) || Date.now())' in worker

cfg = json.loads(re.sub(r'//.*', '', wrangler))
assert cfg.get('triggers', {}).get('crons') == ['*/15 * * * *']

# Execute the actual trigger body extracted from the Worker against SQLite.
match = re.search(r'CREATE TRIGGER IF NOT EXISTS players_queue_displaced_replay[\s\S]*?END', worker)
assert match, 'maintenance trigger SQL missing'
trigger_sql = match.group(0)
con = sqlite3.connect(':memory:')
con.executescript('''
CREATE TABLE players (
  id TEXT PRIMARY KEY,
  updated_at INTEGER NOT NULL,
  best_replay_hash TEXT
);
CREATE TABLE replay_gc_queue (
  hash TEXT PRIMARY KEY,
  queued_at INTEGER NOT NULL
);
''')
con.execute(trigger_sql)
con.execute("INSERT INTO players(id,updated_at,best_replay_hash) VALUES('p',100,'h0')")
con.execute("UPDATE players SET best_replay_hash='ha',updated_at=200 WHERE id='p'")
con.execute("UPDATE players SET best_replay_hash='hb',updated_at=300 WHERE id='p'")
rows = con.execute('SELECT hash,queued_at FROM replay_gc_queue ORDER BY hash').fetchall()
assert rows == [('h0', 200), ('ha', 300)], rows

# Verify the cleanup predicates preserve recent rows and remove only retained-age rows.
con.executescript('''
CREATE TABLE run_tickets (
  id TEXT PRIMARY KEY,
  expires_at INTEGER NOT NULL,
  used_at INTEGER
);
''')
now = 10_000_000
retention = 7 * 24 * 60 * 60 * 1000
cutoff = now - retention
# Use a larger synthetic now so positive timestamps are convenient.
now = retention + 1_000_000
cutoff = now - retention
con.executemany('INSERT INTO run_tickets(id,expires_at,used_at) VALUES(?,?,?)', [
  ('used-old', now + 1, cutoff - 1),
  ('used-recent', now + 1, cutoff + 1),
  ('abandoned-old', cutoff - 1, None),
  ('abandoned-recent', cutoff + 1, None),
])
con.execute('DELETE FROM run_tickets WHERE id IN (SELECT id FROM run_tickets WHERE used_at IS NOT NULL AND used_at < ? ORDER BY used_at ASC LIMIT ?)', (cutoff, 500))
con.execute('DELETE FROM run_tickets WHERE id IN (SELECT id FROM run_tickets WHERE used_at IS NULL AND expires_at < ? ORDER BY expires_at ASC LIMIT ?)', (cutoff, 500))
remaining = {r[0] for r in con.execute('SELECT id FROM run_tickets')}
assert remaining == {'used-recent', 'abandoned-recent'}, remaining

print('F12 backend maintenance and replay GC regression PASS')
