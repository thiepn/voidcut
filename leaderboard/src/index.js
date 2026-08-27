import { DurableObject } from 'cloudflare:workers';
import { verifyReplay } from './generated-verifier.js';

const RULESET = Object.freeze({ build: '6.1.0', replay: 9, arena: 2, director: 6 });
const TICKET_TTL_MS = 6 * 60 * 60 * 1000;
const TICKET_RETENTION_MS = 7 * 24 * 60 * 60 * 1000;
const TICKET_CLEANUP_BATCH = 500;
const REPLAY_GC_GRACE_MS = 24 * 60 * 60 * 1000;
const REPLAY_GC_BATCH = 50;
const MAX_REPLAY_BYTES = 2_500_000;
const MAX_COMPETITIVE_EVENTS = 12_000;
const MAX_COMPETITIVE_DURATION = 1_800;
const NAME_RE = /^[A-Za-z0-9 _-]{3,16}$/;
const RESERVED_NAMES = new Set(['ADMIN', 'MOD', 'MODERATOR', 'SYSTEM', 'VOIDCUT', 'DEVELOPER', 'STAFF']);
const ALLOWED_ORIGINS = new Set([
  'https://thiepn.dev',
  'https://www.thiepn.dev',
  'https://thiepn.github.io',
]);

let schemaPromise = null;
function ensureSchema(env) {
  if (!schemaPromise) {
    schemaPromise = env.DB.batch([
      env.DB.prepare(`CREATE TABLE IF NOT EXISTS players (
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
      )`),
      env.DB.prepare('CREATE INDEX IF NOT EXISTS players_leaderboard_idx ON players(best_score DESC, best_chamber DESC, best_time ASC, updated_at ASC)'),
      env.DB.prepare(`CREATE TABLE IF NOT EXISTS run_tickets (
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
      )`),
      env.DB.prepare('CREATE INDEX IF NOT EXISTS run_tickets_expiry_idx ON run_tickets(expires_at)'),
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
      schemaPromise = null;
      throw err;
    });
  }
  return schemaPromise;
}

function allowedOrigin(request) {
  const origin = request.headers.get('Origin');
  if (!origin) return '*';
  if (ALLOWED_ORIGINS.has(origin)) return origin;
  if (/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(origin)) return origin;
  return null;
}
function corsHeaders(request) {
  const origin = allowedOrigin(request);
  return {
    ...(origin ? { 'Access-Control-Allow-Origin': origin } : {}),
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Max-Age': '86400',
    'Cache-Control': 'no-store',
    'Content-Type': 'application/json; charset=utf-8',
    'Vary': 'Origin',
  };
}
function json(request, data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: corsHeaders(request) });
}
function error(request, status, code, message = code) {
  return json(request, { ok: false, error: code, message }, status);
}
function cleanName(value) {
  const name = String(value ?? '').trim().replace(/\s+/g, ' ');
  if (!NAME_RE.test(name) || RESERVED_NAMES.has(name.toUpperCase())) return null;
  return name;
}
function randomToken(bytes = 32) {
  const b = new Uint8Array(bytes);
  crypto.getRandomValues(b);
  let s = '';
  for (const x of b) s += String.fromCharCode(x);
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}
async function sha256(text) {
  const bytes = new TextEncoder().encode(text);
  const digest = new Uint8Array(await crypto.subtle.digest('SHA-256', bytes));
  return [...digest].map(x => x.toString(16).padStart(2, '0')).join('');
}
function bearer(request) {
  const h = request.headers.get('Authorization') || '';
  return h.startsWith('Bearer ') ? h.slice(7).trim() : '';
}
async function authenticate(request, env, required = true) {
  const token = bearer(request);
  if (!token) return required ? null : null;
  const tokenHash = await sha256(token);
  return env.DB.prepare('SELECT id,name,best_score,best_chamber,best_time,best_grade,best_replay_hash FROM players WHERE token_hash=? LIMIT 1').bind(tokenHash).first();
}
function randomSeed() {
  const a = new Uint32Array(1);
  crypto.getRandomValues(a);
  return a[0] >>> 0;
}
async function readJson(request, maxBytes = 32_000) {
  const len = Number(request.headers.get('Content-Length') || 0);
  if (len && len > maxBytes) throw new Error('body-too-large');
  const text = await request.text();
  if (text.length > maxBytes) throw new Error('body-too-large');
  return text ? JSON.parse(text) : {};
}
async function readBoundedText(request, maxBytes) {
  const len = Number(request.headers.get('Content-Length') || 0);
  if (len && len > maxBytes) throw new Error('body-too-large');
  if (!request.body) return '';
  const reader = request.body.getReader();
  const decoder = new TextDecoder();
  let total = 0;
  let text = '';
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value?.byteLength || 0;
      if (total > maxBytes) throw new Error('body-too-large');
      text += decoder.decode(value, { stream: true });
    }
    text += decoder.decode();
    return text;
  } catch (err) {
    try { await reader.cancel(); } catch {}
    throw err;
  }
}
function preauthKey(request) {
  const ip = String(request.headers.get('CF-Connecting-IP') || '').trim();
  return `ip:${ip || 'unknown'}`;
}
function compareLeaderboardRank(a,b){const scoreA=Number.isFinite(Number(a?.score))?Number(a.score):0,scoreB=Number.isFinite(Number(b?.score))?Number(b.score):0;if(scoreA!==scoreB)return scoreA>scoreB?-1:1;const chamberA=a?.chamber==null?1:Number.isFinite(Number(a.chamber))?Number(a.chamber):1,chamberB=b?.chamber==null?1:Number.isFinite(Number(b.chamber))?Number(b.chamber):1;if(chamberA!==chamberB)return chamberA>chamberB?-1:1;const timeA=a?.time==null?Infinity:Number.isFinite(Number(a.time))?Number(a.time):Infinity,timeB=b?.time==null?Infinity:Number.isFinite(Number(b.time))?Number(b.time):Infinity;if(timeA!==timeB)return timeA<timeB?-1:1;const updatedA=a?.updatedAt==null?Infinity:Number.isFinite(Number(a.updatedAt))?Number(a.updatedAt):Infinity,updatedB=b?.updatedAt==null?Infinity:Number.isFinite(Number(b.updatedAt))?Number(b.updatedAt):Infinity;if(updatedA!==updatedB)return updatedA<updatedB?-1:1;const idA=String(a?.id??''),idB=String(b?.id??'');if(idA!==idB)return idA<idB?-1:1;return 0}
async function rankForPlayer(env, player) {
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
async function playerSnapshot(env, id) {
  if (!id) return null;
  return env.DB.prepare('SELECT id,name,best_score,best_chamber,best_time,best_grade,best_replay_hash,updated_at FROM players WHERE id=? LIMIT 1').bind(id).first();
}

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

async function createProfile(request, env) {
  const { success } = await env.PROFILE_LIMIT.limit({ key: preauthKey(request) });
  if (!success) return error(request, 429, 'rate-limited', 'Too many profile attempts.');
  let body;
  try { body = await readJson(request); } catch { return error(request, 400, 'invalid-body', 'Invalid profile request.'); }
  const name = cleanName(body.name);
  if (!name) return error(request, 400, 'invalid-name', 'Use 3–16 letters, numbers, spaces, underscores or hyphens.');
  const id = crypto.randomUUID();
  const token = randomToken();
  const tokenHash = await sha256(token);
  const now = Date.now();
  try {
    await env.DB.prepare('INSERT INTO players(id,name,token_hash,created_at,updated_at) VALUES(?,?,?,?,?)').bind(id, name, tokenHash, now, now).run();
  } catch (err) {
    if (/UNIQUE|constraint/i.test(String(err))) return error(request, 409, 'name-taken', 'That leaderboard name is already taken.');
    throw err;
  }
  return json(request, { ok: true, player: { id, name }, token });
}

async function startRun(request, env) {
  const token = bearer(request);
  const player = token ? await authenticate(request, env, false) : null;
  if (token && !player) return error(request, 401, 'invalid-profile', 'Leaderboard identity is invalid.');
  const key = player?.id || preauthKey(request);
  const { success } = await env.RUN_LIMIT.limit({ key });
  if (!success) return error(request, 429, 'rate-limited', 'Too many run tickets requested.');
  const id = crypto.randomUUID();
  const seed = randomSeed();
  const now = Date.now();
  const expiresAt = now + TICKET_TTL_MS;
  await env.DB.prepare('INSERT INTO run_tickets(id,seed,player_id,created_at,expires_at,status) VALUES(?,?,?,?,?,?)')
    .bind(id, seed, player?.id || null, now, expiresAt, 'issued').run();
  return json(request, { ok: true, ticketId: id, seed, expiresAt, ruleset: RULESET, ranked: true });
}

async function leaderboard(request, env) {
  const url = new URL(request.url);
  const limit = Math.max(1, Math.min(100, Number(url.searchParams.get('limit')) || 100));
  const result = await env.DB.prepare(`SELECT id,name,best_score AS score,best_chamber AS chamber,best_time AS time,best_grade AS grade,best_replay_hash AS replayHash,updated_at AS updatedAt
    FROM players WHERE best_score>0
    ORDER BY best_score DESC,best_chamber DESC,COALESCE(best_time,1e99) ASC,updated_at ASC,id ASC LIMIT ?`).bind(limit).all();
  const ordered = (result.results || []).sort(compareLeaderboardRank);
  const rows = ordered.map(({ updatedAt, ...r }, i) => ({ rank: i + 1, ...r }));
  let self = null;
  const playerId = url.searchParams.get('player_id');
  if (playerId) {
    const p = await playerSnapshot(env, playerId);
    if (p) self = {
      id: p.id,
      name: p.name,
      score: p.best_score,
      chamber: p.best_chamber,
      time: p.best_time,
      grade: p.best_grade,
      replayHash: p.best_replay_hash,
      rank: await rankForPlayer(env, p),
    };
  }
  return json(request, { ok: true, ruleset: RULESET, rows, self });
}

function normalizeReplayHash(value) {
  const hash = String(value ?? '').toLowerCase();
  return /^[a-f0-9]{64}$/.test(hash) ? hash : null;
}
async function replayResponse(request, env, hash) {
  const replayHash = normalizeReplayHash(hash);
  if (!replayHash) return error(request, 400, 'invalid-replay', 'Invalid replay id.');
  const owner = await env.DB.prepare('SELECT id FROM players WHERE best_replay_hash=? LIMIT 1').bind(replayHash).first();
  if (!owner) return error(request, 404, 'not-found', 'Replay is not on the leaderboard.');
  const obj = await env.REPLAYS.get(`verified/${replayHash}.json`);
  if (!obj) return error(request, 404, 'not-found', 'Replay data is unavailable.');
  const headers = corsHeaders(request);
  headers['Content-Type'] = 'application/json; charset=utf-8';
  headers['Cache-Control'] = 'public, max-age=300';
  return new Response(obj.body, { headers });
}

async function forwardSubmission(request, env, ticketId) {
  const token = bearer(request);
  if (!token) return error(request, 401, 'profile-required', 'Create a leaderboard profile first.');
  const { success } = await env.SUBMIT_LIMIT.limit({ key: preauthKey(request) });
  if (!success) return error(request, 429, 'rate-limited', 'Too many score submissions.');
  const len = Number(request.headers.get('Content-Length') || 0);
  if (len && len > MAX_REPLAY_BYTES) return error(request, 413, 'replay-too-large', 'Replay is too large.');
  const stub = env.VERIFIER.getByName(ticketId);
  const headers = new Headers(request.headers);
  headers.set('x-voidcut-ticket', ticketId);
  return stub.fetch(new Request('https://voidcut-verifier/verify', { method: 'POST', headers, body: request.body }));
}

export class ReplayVerifier extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.env = env;
  }

  async fetch(request) {
    await ensureSchema(this.env);
    const ticketId = request.headers.get('x-voidcut-ticket') || '';
    const player = await authenticate(request, this.env, true);
    if (!player) return error(request, 401, 'invalid-profile', 'Leaderboard identity is invalid.');
    const ticket = await this.env.DB.prepare('SELECT * FROM run_tickets WHERE id=? LIMIT 1').bind(ticketId).first();
    if (!ticket) return error(request, 404, 'invalid-ticket', 'Run ticket was not found.');
    if (ticket.player_id && ticket.player_id !== player.id) return error(request, 403, 'ticket-owner-mismatch', 'This run ticket belongs to another leaderboard profile.');
    if (ticket.status === 'verified') {
      const p = await playerSnapshot(this.env, player.id);
      return json(request, { ok: true, verified: true, personalBest: p?.best_replay_hash === ticket.replay_hash, score: ticket.result_score, chamber: ticket.result_chamber, grade: ticket.result_grade, replayHash: ticket.replay_hash, rank: await rankForPlayer(this.env, p) });
    }
    if (ticket.status === 'rejected' || ticket.used_at) return error(request, 409, 'ticket-used', 'This run ticket has already been consumed.');
    if (Date.now() > Number(ticket.expires_at)) {
      await this.env.DB.prepare("UPDATE run_tickets SET status='expired',used_at=? WHERE id=? AND used_at IS NULL").bind(Date.now(), ticketId).run();
      return error(request, 410, 'ticket-expired', 'This ranked run ticket expired.');
    }

    let text;
    try {
      text = await readBoundedText(request, MAX_REPLAY_BYTES);
    } catch {
      return error(request, 413, 'replay-too-large', 'Replay is too large.');
    }
    let replay;
    try { replay = JSON.parse(text); } catch { return this.#reject(request, ticketId, 'invalid-json', 'Replay payload is invalid.'); }
    if (replay?.version !== RULESET.replay || (replay?.arenaGeneration || 2) !== RULESET.arena || (replay?.directorGeneration || 6) !== RULESET.director) {
      return this.#reject(request, ticketId, 'wrong-ruleset', 'Only current VOIDCUT competitive runs can enter the global leaderboard.');
    }
    if ((replay.seed >>> 0) !== (Number(ticket.seed) >>> 0)) return this.#reject(request, ticketId, 'seed-mismatch', 'Replay seed does not match its server-issued run ticket.');
    if (!Array.isArray(replay.events) || replay.events.length > MAX_COMPETITIVE_EVENTS || !Number.isFinite(replay.deathTime) || replay.deathTime < 0 || replay.deathTime > MAX_COMPETITIVE_DURATION) {
      return this.#reject(request, ticketId, 'replay-resource-limit', 'Replay exceeds competitive verification limits.');
    }

    const official = verifyReplay(replay);
    if (!official) return this.#reject(request, ticketId, 'verification-failed', 'Deterministic replay verification failed.');

    const serverReplayHash = await sha256(text);
    const now = Date.now();
    const old = await playerSnapshot(this.env, player.id);
    const better = !old || compareLeaderboardRank(
      {score:official.score,chamber:official.chamber,time:official.deathTime},
      {score:old.best_score,chamber:old.best_chamber,time:old.best_time}
    ) < 0;

    let personalBest = false;
    if (better) {
      await queueReplayForGc(this.env, serverReplayHash, now);
      await this.env.REPLAYS.put(`verified/${serverReplayHash}.json`, JSON.stringify(replay), { httpMetadata: { contentType: 'application/json' } });
      const update = await this.env.DB.prepare(`UPDATE players SET best_score=?,best_chamber=?,best_time=?,best_grade=?,best_replay_hash=?,updated_at=?
        WHERE id=? AND (
          best_score < ? OR
          (best_score = ? AND best_chamber < ?) OR
          (best_score = ? AND best_chamber = ? AND (best_time IS NULL OR best_time > ?))
        )`)
        .bind(official.score, official.chamber, official.deathTime, official.bestGrade, serverReplayHash, now, player.id,
          official.score, official.score, official.chamber, official.score, official.chamber, official.deathTime).run();
      personalBest = Number(update?.meta?.changes || 0) > 0;
    }

    await this.env.DB.prepare(`UPDATE run_tickets SET player_id=?,used_at=?,status='verified',result_score=?,result_chamber=?,result_time=?,result_grade=?,replay_hash=? WHERE id=? AND used_at IS NULL`)
      .bind(player.id, now, official.score, official.chamber, official.deathTime, official.bestGrade, serverReplayHash, ticketId).run();
    const current = await playerSnapshot(this.env, player.id);
    return json(request, {
      ok: true,
      verified: true,
      personalBest,
      score: official.score,
      chamber: official.chamber,
      grade: official.bestGrade,
      replayHash: serverReplayHash,
      rank: await rankForPlayer(this.env, current),
    });
  }

  async #reject(request, ticketId, code, message) {
    await this.env.DB.prepare("UPDATE run_tickets SET used_at=?,status='rejected' WHERE id=? AND used_at IS NULL").bind(Date.now(), ticketId).run();
    return error(request, 422, code, message);
  }
}

export default {
  async fetch(request, env) {
    const origin = allowedOrigin(request);
    if (request.method === 'OPTIONS') {
      if (!origin) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: corsHeaders(request) });
    }
    if (!origin) return error(request, 403, 'origin-denied', 'Origin is not allowed.');
    const url = new URL(request.url);
    try {
      await ensureSchema(env);
      if (request.method === 'GET' && url.pathname === '/health') return json(request, { ok: true, service: 'voidcut-leaderboard', ruleset: RULESET });
      if (request.method === 'POST' && url.pathname === '/profile/create') return await createProfile(request, env);
      if (request.method === 'POST' && url.pathname === '/run/start') return await startRun(request, env);
      if (request.method === 'POST' && url.pathname.startsWith('/run/submit/')) {
        const ticketId = url.pathname.slice('/run/submit/'.length);
        if (!/^[0-9a-f-]{36}$/i.test(ticketId)) return error(request, 400, 'invalid-ticket', 'Invalid run ticket.');
        return await forwardSubmission(request, env, ticketId);
      }
      if (request.method === 'GET' && url.pathname === '/leaderboard') return await leaderboard(request, env);
      if (request.method === 'GET' && url.pathname.startsWith('/replay/')) return await replayResponse(request, env, url.pathname.slice('/replay/'.length).toLowerCase());
      return error(request, 404, 'not-found', 'Unknown leaderboard endpoint.');
    } catch (err) {
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
