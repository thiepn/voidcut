CREATE TABLE IF NOT EXISTS players (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL COLLATE NOCASE UNIQUE,
  token_hash TEXT NOT NULL UNIQUE,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL,
  best_score INTEGER NOT NULL DEFAULT 0,
  best_chamber INTEGER NOT NULL DEFAULT 1,
  best_time REAL,
  best_grade TEXT,
  best_replay_hash TEXT
);

CREATE INDEX IF NOT EXISTS players_leaderboard_idx
ON players(best_score DESC, best_chamber DESC, best_time ASC, updated_at ASC);

CREATE TABLE IF NOT EXISTS run_tickets (
  id TEXT PRIMARY KEY,
  seed INTEGER NOT NULL,
  player_id TEXT,
  created_at INTEGER NOT NULL,
  expires_at INTEGER NOT NULL,
  used_at INTEGER,
  status TEXT NOT NULL DEFAULT 'issued',
  result_score INTEGER,
  result_chamber INTEGER,
  result_time REAL,
  result_grade TEXT,
  replay_hash TEXT,
  FOREIGN KEY(player_id) REFERENCES players(id)
);

CREATE INDEX IF NOT EXISTS run_tickets_expiry_idx
ON run_tickets(expires_at);
