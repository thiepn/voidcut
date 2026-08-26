from pathlib import Path

p = Path(__file__).resolve().parents[2] / 'leaderboard' / 'scripts' / 'test-ranked-start-ticket-source.mjs'
s = p.read_text(encoding='utf-8')
old = r"""const helperPattern = /async function acquireLeaderboardTicket\(waitMs=RANKED_START_WAIT_MS\)\{[\s\S]*?\}\nfunction invalidateRankedRun/;
const inlineHelperEnvelope = html.match(helperPattern);
assert.ok(inlineHelperEnvelope, 'inline acquireLeaderboardTicket helper missing');
const inlineHelper = inlineHelperEnvelope[0].replace(/\nfunction invalidateRankedRun[\s\S]*$/, '');
const clientHelperMatch = client.match(/async function acquireLeaderboardTicket\(waitMs=RANKED_START_WAIT_MS\)\{[^\n]+\}/);
"""
new = r"""const helperPattern = /async function acquireLeaderboardTicket\(waitMs=RANKED_START_WAIT_MS\)\{[^\n]+\}/;
const inlineHelperMatch = html.match(helperPattern);
assert.ok(inlineHelperMatch, 'inline acquireLeaderboardTicket helper missing');
const inlineHelper = inlineHelperMatch[0];
const clientHelperMatch = client.match(helperPattern);
"""
if s.count(old) != 1:
    raise SystemExit(f'F8 helper extraction compatibility: expected 1 match, found {s.count(old)}')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
