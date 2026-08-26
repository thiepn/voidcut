from pathlib import Path

root = Path(__file__).resolve().parents[2]
worker = root / 'leaderboard' / 'src' / 'index.js'
register = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

w = worker.read_text(encoding='utf-8')
old = """async function replayResponse(request, env, hash) {
  if (!/^[A-F0-9]{64}$/.test(hash)) return error(request, 400, 'invalid-replay', 'Invalid replay id.');
  const owner = await env.DB.prepare('SELECT id FROM players WHERE best_replay_hash=? LIMIT 1').bind(hash).first();
  if (!owner) return error(request, 404, 'not-found', 'Replay is not on the leaderboard.');
  const obj = await env.REPLAYS.get(`verified/${hash}.json`);
  if (!obj) return error(request, 404, 'not-found', 'Replay data is unavailable.');
  const headers = corsHeaders(request);
  headers['Content-Type'] = 'application/json; charset=utf-8';
  headers['Cache-Control'] = 'public, max-age=300';
  return new Response(obj.body, { headers });
}
"""
new = """function normalizeReplayHash(value) {
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
"""
w = replace_once(w, old, new, 'replay response canonicalization')
worker.write_text(w, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old_row = '| VC-005 | HIGH | Global replay retrieval lowercases hashes but validates with an uppercase-only hexadecimal regex. | F5 | OPEN |'
new_row = '| VC-005 | HIGH | Global replay retrieval lowercases hashes but validates with an uppercase-only hexadecimal regex. | F5 | FIXED — VERIFYING |'
if r.count(old_row) != 1:
    raise SystemExit('VC-005 register marker missing')
r = r.replace(old_row, new_row, 1)
r += '''\n## F5 implementation record — canonical replay hash retrieval\n\n- Global replay IDs are now normalized exactly once to lowercase before validation and lookup.\n- The canonical validator accepts only 64 hexadecimal characters after normalization.\n- Both lowercase and uppercase request forms resolve to the same canonical lowercase SHA-256 identifier.\n- D1 `best_replay_hash` lookup and R2 `verified/<hash>.json` lookup now use the same canonical lowercase value.\n- This matches the existing `sha256()` implementation, which emits lowercase hexadecimal, and the route layer, which already lowercases `/replay/<hash>` path values.\n- Invalid length/non-hex replay IDs still fail with `invalid-replay`.\n\nF5 changes only global replay retrieval normalization; replay generation, verification, scoring, storage format, save schema and gameplay are unchanged.\n'''
register.write_text(r, encoding='utf-8')
