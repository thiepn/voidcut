from pathlib import Path

worker_path = Path('leaderboard/src/index.js')
worker = worker_path.read_text(encoding='utf-8')

replacements = [
    (
        """async function startRun(request, env) {\n  const token = bearer(request);\n  let player = null;\n  if (token) player = await authenticate(request, env, false);\n  const key = player?.id || preauthKey(request);""",
        """async function startRun(request, env) {\n  const token = bearer(request);\n  const player = token ? await authenticate(request, env, false) : null;\n  if (token && !player) return error(request, 401, 'invalid-profile', 'Leaderboard identity is invalid.');\n  const key = player?.id || preauthKey(request);""",
        'invalid bearer fallback hardening',
    ),
    (
        """  const tokenKey = await sha256(token);\n  const { success } = await env.SUBMIT_LIMIT.limit({ key: tokenKey });""",
        """  const { success } = await env.SUBMIT_LIMIT.limit({ key: preauthKey(request) });""",
        'submission limiter anti-rotation hardening',
    ),
    (
        """    if (!ticket) return error(request, 404, 'invalid-ticket', 'Run ticket was not found.');\n    if (ticket.status === 'verified') {""",
        """    if (!ticket) return error(request, 404, 'invalid-ticket', 'Run ticket was not found.');\n    if (ticket.player_id && ticket.player_id !== player.id) return error(request, 403, 'ticket-owner-mismatch', 'This run ticket belongs to another leaderboard profile.');\n    if (ticket.status === 'verified') {""",
        'verified ticket ownership hardening',
    ),
    (
        """    if (ticket.player_id && ticket.player_id !== player.id) return error(request, 403, 'ticket-owner-mismatch', 'This run ticket belongs to another leaderboard profile.');\n\n    let text;""",
        """\n    let text;""",
        'remove late duplicate ownership check',
    ),
]
for old, new, label in replacements:
    count = worker.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    worker = worker.replace(old, new, 1)
worker_path.write_text(worker, encoding='utf-8')

workflow_path = Path('.github/workflows/cross-browser-release.yml')
workflow = workflow_path.read_text(encoding='utf-8')

old_source = """      - name: Run F21 suite contract regression\n        working-directory: leaderboard\n        run: node scripts/test-cross-browser-release-suite-source.mjs\n\n  browser-matrix:"""
new_source = """      - name: Run F21 suite contract regression\n        working-directory: leaderboard\n        run: node scripts/test-cross-browser-release-suite-source.mjs\n\n      - name: Run F22 adversarial suite contract regression\n        working-directory: leaderboard\n        run: node scripts/test-adversarial-release-suite-source.mjs\n\n  adversarial-leaderboard:\n    name: F22 adversarial leaderboard / anti-cheat gate\n    needs: source-regressions\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n\n      - uses: actions/setup-node@v4\n        with:\n          node-version: '22'\n\n      - name: Install verifier build dependencies\n        working-directory: leaderboard\n        run: npm install --ignore-scripts --no-audit --no-fund\n\n      - name: Run adversarial leaderboard corpus\n        working-directory: leaderboard\n        run: npm run test:adversarial\n\n      - name: Recheck ranked timing/resource/rate/ranking defenses\n        working-directory: leaderboard\n        run: |\n          node scripts/test-replay-timing-source.mjs ../index.html\n          node scripts/test-replay-resource-limits-source.mjs ../index.html\n          node scripts/test-anonymous-rate-limit-source.mjs\n          node scripts/test-ranked-start-ticket-source.mjs\n          node scripts/test-leaderboard-ranking-source.mjs\n          python3 scripts/test-backend-maintenance-source.py\n\n  browser-matrix:"""
if workflow.count(old_source) != 1:
    raise SystemExit(f'workflow F22 insertion point: expected 1 match, found {workflow.count(old_source)}')
workflow = workflow.replace(old_source, new_source, 1)

old_needs = """  browser-matrix:\n    name: Browser certification / ${{ matrix.browser }}\n    needs: source-regressions"""
new_needs = """  browser-matrix:\n    name: Browser certification / ${{ matrix.browser }}\n    needs: [source-regressions, adversarial-leaderboard]"""
if workflow.count(old_needs) != 1:
    raise SystemExit(f'browser F22 dependency: expected 1 match, found {workflow.count(old_needs)}')
workflow = workflow.replace(old_needs, new_needs, 1)
workflow_path.write_text(workflow, encoding='utf-8')
