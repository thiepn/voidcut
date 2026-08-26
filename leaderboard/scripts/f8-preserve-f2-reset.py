from pathlib import Path

p = Path(__file__).resolve().parents[2] / 'index.html'
s = p.read_text(encoding='utf-8')
old = "activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;rankedRunInvalidReason=!challenge&&!activeLeaderboardTicket?(rankedStartReason||'LEADERBOARD UNAVAILABLE'):null;rankedRunInvalidNoticeShown=false;resetRankedTimingIntegrity();"
new = "activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;rankedRunInvalidReason=null;rankedRunInvalidNoticeShown=false;if(!challenge&&!activeLeaderboardTicket)rankedRunInvalidReason=rankedStartReason||'LEADERBOARD UNAVAILABLE';resetRankedTimingIntegrity();"
if s.count(old) != 1:
    raise SystemExit(f'F8/F2 reset compatibility: expected 1 match, found {s.count(old)}')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
