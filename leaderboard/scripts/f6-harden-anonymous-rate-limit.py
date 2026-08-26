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
old = """function preauthKey(request) {
  return `${request.headers.get('CF-Connecting-IP') || 'unknown'}|${(request.headers.get('User-Agent') || '').slice(0, 96)}`;
}
"""
new = """function preauthKey(request) {
  const ip = String(request.headers.get('CF-Connecting-IP') || '').trim();
  return `ip:${ip || 'unknown'}`;
}
"""
w = replace_once(w, old, new, 'anonymous rate-limit identity')
worker.write_text(w, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old_row = '| VC-006 | HIGH | Anonymous rate-limit identity uses IP + attacker-controlled User-Agent and is trivially splittable. | F6 | OPEN |'
new_row = '| VC-006 | HIGH | Anonymous rate-limit identity uses IP + attacker-controlled User-Agent and is trivially splittable. | F6 | FIXED — VERIFYING |'
if r.count(old_row) != 1:
    raise SystemExit('VC-006 register marker missing')
r = r.replace(old_row, new_row, 1)
r += '''\n## F6 implementation record — stable anonymous rate-limit identity\n\n- Anonymous profile-creation and run-ticket rate limits now key only on Cloudflare's server-provided `CF-Connecting-IP`; attacker-controlled `User-Agent` is no longer part of rate-limit identity.\n- The key is namespaced as `ip:<address>` so its meaning is explicit and cannot be confused with authenticated player/token identities.\n- Requests without a `CF-Connecting-IP` use the stable fail-closed bucket `ip:unknown` rather than a caller-controlled fallback header.\n- Rotating, randomizing or omitting `User-Agent` therefore cannot create additional anonymous profile/run rate-limit buckets.\n- Authenticated run tickets continue to use the authenticated player ID, and score submission throttling continues to use the SHA-256 of the bearer token; F6 does not weaken authenticated throttling.\n- Existing Cloudflare rate-limit quotas and namespaces remain unchanged.\n\nF6 changes only anonymous rate-limit identity construction; authentication tokens, leaderboard rules, replay verification, scoring, storage, save schema and gameplay are unchanged.\n'''
register.write_text(r, encoding='utf-8')
