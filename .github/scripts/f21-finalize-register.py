from pathlib import Path

p = Path('design/V6_2_HARDENING_FIX_REGISTER.md')
s = p.read_text(encoding='utf-8')

replacements = [
    (
        '| VC-025 | HIGH | Current v6.1/save17/replay9 code has not been run through the old full cross-browser/PWA certification suite. | F21 | OPEN |',
        '| VC-025 | HIGH | Current v6.1/save17/replay9 code has not been run through the old full cross-browser/PWA certification suite. | F21 | FIXED — F21 PASS |',
        'VC-025 row',
    ),
    (
        '| F21 | Restore automated cross-browser release suite for current contracts | NOT STARTED |',
        '| F21 | Restore automated cross-browser release suite for current contracts | PASS |',
        'F21 gate row',
    ),
]
for old, new, label in replacements:
    if s.count(old) != 1:
        raise SystemExit(f'{label}: expected 1 match, found {s.count(old)}')
    s = s.replace(old, new, 1)

s += '''\n## F21 implementation record — automated current-contract cross-browser certification\n\n- Restored a persistent Playwright-based browser release suite in the repository, pinned to `@playwright/test` 1.62.1 and configured for Chromium, Firefox and WebKit/Safari-equivalent behavior.\n- The suite serves the hardening checkout locally and fixtures leaderboard reads/tickets inside the browser process, so certification does not mutate the production deployment or production leaderboard.\n- A permanent source/regression job runs service-worker, Worker and inline-runtime syntax plus all F1-F21 source regressions before browser jobs are allowed to start.\n- Each browser runs in an isolated CI job with failure traces, screenshots, video and reports retained as artifacts when a test fails.\n- Real-browser coverage includes current release metadata (build 6.1.0, save 17, replay 9, arena 2, director 6), desktop/mobile responsive bounds, transactional save persistence through a UI setting change and reload, keyboard pause/resume, real mouse pointer input, native touch input, and uncaught page-error detection.\n- The browser suite runs the built-in FULL RELEASE CHECK and requires the current deterministic/replay contract checks to pass, including strict replay-v9 input timing, high-score replay round-trip and same-seed determinism.\n- The PWA test changes only the isolated checkout's service-worker bytes, calls `registration.update()`, proves the update reaches `registration.waiting` without replacing the active controller, verifies the UI exposes `UPDATE READY`, and then proves activation/reload occurs only after the explicit update button is pressed.\n- Two harness defects were caught before certification was accepted: the first seed helper overwrote the saved setting again on reload, and synthetic DOM PointerEvents did not establish a browser-native pointer eligible for `setPointerCapture`. The final suite seeds only an absent save and uses Playwright's native touchscreen input while keeping a separate real mouse-drag path. Production behavior was not weakened to accommodate either test artifact.\n- Final certification workflow `33074270574` passed its F1-F21 source gate and all three browser jobs: Chromium PASS, Firefox PASS and WebKit PASS.\n\n**F21 disposition: PASS. VC-025 closed.**\n'''

p.write_text(s, encoding='utf-8')
