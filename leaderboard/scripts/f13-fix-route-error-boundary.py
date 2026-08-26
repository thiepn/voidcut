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
replacements = [
    ("return createProfile(request, env);", "return await createProfile(request, env);", 'profile route await'),
    ("return startRun(request, env);", "return await startRun(request, env);", 'run-start route await'),
    ("return forwardSubmission(request, env, ticketId);", "return await forwardSubmission(request, env, ticketId);", 'submission route await'),
    ("return leaderboard(request, env);", "return await leaderboard(request, env);", 'leaderboard route await'),
    ("return replayResponse(request, env, url.pathname.slice('/replay/'.length).toLowerCase());", "return await replayResponse(request, env, url.pathname.slice('/replay/'.length).toLowerCase());", 'replay route await'),
]
for old, new, label in replacements:
    w = replace_once(w, old, new, label)
worker.write_text(w, encoding='utf-8')

r = register.read_text(encoding='utf-8')
old_row = '| VC-015 | MEDIUM | Top-level Worker route try/catch does not await async route handlers consistently, weakening controlled error handling. | F13 | OPEN |'
new_row = '| VC-015 | MEDIUM | Top-level Worker route try/catch does not await async route handlers consistently, weakening controlled error handling. | F13 | FIXED — VERIFYING |'
r = replace_once(r, old_row, new_row, 'VC-015 register row')
r += '''\n## F13 implementation record — awaited top-level Worker route boundary\n\n- Every asynchronous route handler dispatched from the top-level Worker `fetch()` try/catch is now returned with `return await`, so a handler rejection is observed while execution is still inside the controlled error boundary.\n- The affected routes are `/profile/create`, `/run/start`, `/run/submit/:ticket`, `/leaderboard`, and `/replay/:hash`.\n- Synchronous health, OPTIONS, validation, 404 and error-response branches remain direct returns.\n- The F12 scheduled maintenance handler already awaited `ensureSchema()` and `runLeaderboardMaintenance()` inside its own try/catch and was not changed.\n- Route URLs, HTTP status codes, successful response payloads, authentication, rate limits, ticket semantics, D1/R2 logic, ranking, replay verification, save schema, gameplay and UI behavior are unchanged.\n'''
register.write_text(r, encoding='utf-8')
