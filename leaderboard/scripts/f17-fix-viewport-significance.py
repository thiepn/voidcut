from pathlib import Path

root = Path(__file__).resolve().parents[2]
index_path = root / 'index.html'
f3_path = root / 'leaderboard' / 'scripts' / 'test-ranked-timing-source.mjs'
register_path = root / 'design' / 'V6_2_HARDENING_FIX_REGISTER.md'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, found {count}')
    return text.replace(old, new, 1)

html = index_path.read_text(encoding='utf-8')
old = "function settleViewport(force=false){clearTimeout(viewportTimer);viewportTimer=setTimeout(()=>{const prev=viewportState||fitViewport(),next=fitViewport(),dw=Math.abs(next.w-prev.w)/Math.max(1,prev.w),dh=Math.abs(next.h-prev.h)/Math.max(1,prev.h),significant=force||next.o!==prev.o||Math.max(dw,dh)>=.12;viewportState=next;trackRankedTimingReset(significant?'DISPLAY CHANGED':'VIEWPORT TIMING RESET',!significant);cancelPointerGesture();acc=0;visualBudget=0;last=performance.now();if(significant){if(state==='play'&&!paused){togglePause(true,'DISPLAY CHANGED');showCoach('DISPLAY CHANGED','Run paused so touch coordinates stay stable.','Global ranking is disabled for this run.',1200)}else if(state==='replay'&&!replayPaused){replayPaused=true;$('replayPause').textContent='RESUME';showCoach('DISPLAY CHANGED','Replay paused while the layout settles.','',900)}}refreshFullscreen()},100)}"
new = "function settleViewport(force=false){clearTimeout(viewportTimer);viewportTimer=setTimeout(()=>{const prev=viewportState||fitViewport(),next=fitViewport(),dw=Math.abs(next.w-prev.w)/Math.max(1,prev.w),dh=Math.abs(next.h-prev.h)/Math.max(1,prev.h),significant=force||next.o!==prev.o||Math.max(dw,dh)>=.12;viewportState=next;if(significant){trackRankedTimingReset('DISPLAY CHANGED');cancelPointerGesture();acc=0;visualBudget=0;last=performance.now();if(state==='play'&&!paused){togglePause(true,'DISPLAY CHANGED');showCoach('DISPLAY CHANGED','Run paused so touch coordinates stay stable.','Global ranking is disabled for this run.',1200)}else if(state==='replay'&&!replayPaused){replayPaused=true;$('replayPause').textContent='RESUME';showCoach('DISPLAY CHANGED','Replay paused while the layout settles.','',900)}}refreshFullscreen()},100)}"
html = replace_once(html, old, new, 'settleViewport significance ordering')
index_path.write_text(html, encoding='utf-8')

# F3 still owns ranked timing reset accounting, but F17 intentionally removes
# insignificant viewport resets from that accounting.
f3 = f3_path.read_text(encoding='utf-8')
old_req = '  "trackRankedTimingReset(significant?\'DISPLAY CHANGED\':\'VIEWPORT TIMING RESET\',!significant)",\n'
new_req = '  "if(significant){trackRankedTimingReset(\'DISPLAY CHANGED\')",\n'
f3 = replace_once(f3, old_req, new_req, 'F3 viewport timing invariant')
f3_path.write_text(f3, encoding='utf-8')

reg = register_path.read_text(encoding='utf-8')
old_row = '| VC-020 | MEDIUM | `visualViewport` resize/scroll handling cancels gestures and resets timing before determining whether the change is significant. | F17 | OPEN |'
new_row = '| VC-020 | MEDIUM | `visualViewport` resize/scroll handling cancels gestures and resets timing before determining whether the change is significant. | F17 | FIXED — VERIFYING |'
reg = replace_once(reg, old_row, new_row, 'VC-020 register row')
reg += '''\n## F17 implementation record — viewport significance before destructive reset\n\n- `settleViewport()` still debounces viewport resize/scroll events, fits the current visual viewport, updates `viewportState`, and uses the existing significance rule: forced change, orientation change, or at least 12% width/height delta.\n- Insignificant viewport changes now stop after geometry/state synchronization and `refreshFullscreen()`. They do not call `trackRankedTimingReset()`, do not cancel the active pointer gesture, do not zero `acc`/`visualBudget`, do not reset `last`, and do not pause play/replay.\n- Significant changes retain the existing safety behavior: ranked timing reset accounting, active-gesture cancellation, timing accumulator reset, play pause/unranking with `DISPLAY CHANGED`, and replay pause.\n- Orientation-change events remain forced significant changes. Regular window resize plus `visualViewport.resize` and `visualViewport.scroll` continue through the same debounced significance gate.\n- F3's permanent ranked-timing regression is updated only to reflect the intended F17 contract: viewport timing-reset accounting is now required inside the significant branch rather than for every viewport event.\n- No gameplay balance, scoring, replay format, save schema, leaderboard backend, PWA cache/update behavior, tutorial state, or visual design changed in F17.\n'''
register_path.write_text(reg, encoding='utf-8')
