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
turnstile_helper = """async function checkTurnstile(request, env, token) {
  if (env.TURNSTILE_REQUIRED !== '1') return true;
  if (!env.TURNSTILE_SECRET || !token) return false;
  const form = new FormData();
  form.set('secret', env.TURNSTILE_SECRET);
  form.set('response', token);
  const ip = request.headers.get('CF-Connecting-IP');
  if (ip) form.set('remoteip', ip);
  const res = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', { method: 'POST', body: form });
  const data = await res.json();
  return data?.success === true;
}
"""
w = replace_once(w, turnstile_helper, '', 'dormant Turnstile helper')
w = replace_once(
    w,
    "  if (!(await checkTurnstile(request, env, body.turnstileToken))) return error(request, 403, 'human-check-failed', 'Human verification failed.');\n",
    '',
    'profile Turnstile gate',
)
worker.write_text(w, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old_row = '| VC-007 | HIGH | Turnstile backend enforcement is implemented without matching client token acquisition/submission. | F7 | OPEN |'
new_row = '| VC-007 | HIGH | Turnstile backend enforcement is implemented without matching client token acquisition/submission. | F7 | FIXED — VERIFYING |'
if r.count(old_row) != 1:
    raise SystemExit('VC-007 register marker missing')
r = r.replace(old_row, new_row, 1)
r += '''\n## F7 implementation record — remove incomplete Turnstile contract\n\n- The dormant Cloudflare Turnstile verification helper and conditional profile-creation gate have been removed from the leaderboard Worker.\n- The shipped client never loaded Turnstile, had no site key/widget/token acquisition path, and submitted profile creation as `{name}` only; retaining a backend-only optional requirement could therefore make legitimate profile creation fail whenever deployment configuration enabled it.\n- F7 deliberately chooses removal rather than adding a new third-party runtime dependency, site-key contract and secret-management requirement late in the hardening cycle.\n- Anonymous abuse protection remains provided by F6's server-controlled `CF-Connecting-IP` rate-limit identity and the existing Cloudflare PROFILE/RUN limiter bindings.\n- Authenticated submission throttling, replay verification and leaderboard identity tokens are unchanged.\n- No client UI, gameplay, scoring, save schema, replay format or release metadata changed.\n\nIf Turnstile is introduced in a future release, it must be implemented as an explicit end-to-end client/server feature with deployment configuration and regression coverage rather than as a dormant backend switch.\n'''
register.write_text(r, encoding='utf-8')
