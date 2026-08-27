from pathlib import Path

p = Path('leaderboard/scripts/test-adversarial-leaderboard.mjs')
s = p.read_text(encoding='utf-8')
old = """const event = base.events[0];\nassert.equal(replayInputTiming(base, event, event.t), 'due');\nassert.equal(replayInputTiming(base, event, event.t + DT), 'stale');\nassert.equal(replayInputTiming(base, event, Math.max(0, event.t - DT)), 'future');"""
new = """const timingEvent = { t: 1 };\nassert.equal(replayInputTiming(base, timingEvent, 1), 'due');\nassert.equal(replayInputTiming(base, timingEvent, 1 + DT), 'stale');\nassert.equal(replayInputTiming(base, timingEvent, 1 - DT), 'future');"""
if s.count(old) != 1:
    raise SystemExit(f'timing fixture: expected 1 match, found {s.count(old)}')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
