from pathlib import Path

p = Path(__file__).resolve().parents[2] / 'leaderboard' / 'scripts' / 'test-ranked-start-ticket-source.mjs'
s = p.read_text(encoding='utf-8')
old = '"let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false,rankedTimingIntegrity=null,rankedStartPromise=null,leaderboardSubmissionQueue=[],leaderboardQueueDrainPromise=null,leaderboardQueueRetryTimer=null;",'
new = '"let leaderboardTicket=null,leaderboardTicketPromise=null,activeLeaderboardTicket=null,rankedRunInvalidReason=null,rankedRunInvalidNoticeShown=false,rankedTimingIntegrity=null,rankedStartPromise=null,leaderboardSubmissionQueue=[],leaderboardQueueDrainPromise=null,leaderboardQueueRetryTimer=null,leaderboardIdentityMemory=null;",'
if s.count(old) != 1:
    raise SystemExit(f'F8 state compatibility: expected 1 match, found {s.count(old)}')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
