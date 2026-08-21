from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'index.html'
text = INDEX.read_text(encoding='utf-8')

if 'name="voidcut-visual-phase" content="VD4"' in text:
    print('VD4 secondary screens already applied')
    raise SystemExit(0)
if 'name="voidcut-visual-phase" content="VD3"' not in text:
    raise SystemExit('Expected VD3 baseline')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    text = text.replace(old, new, 1)


def replace_regex(pattern: str, repl: str, label: str) -> None:
    global text
    text2, count = re.subn(pattern, repl, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one regex match, found {count}')
    text = text2


replace_once('name="voidcut-visual-phase" content="VD3"', 'name="voidcut-visual-phase" content="VD4"', 'visual phase')

records_header = '''<header class="screen-hero records-screen-hero vd4-masthead">
      <div class="screen-hero-copy"><div class="screen-kicker">RUN ARCHIVE</div><div class="pause-title">RECORDS</div><div class="screen-subtitle">Your strongest cuts, clears and survival marks.</div></div>
      <div class="vd4-section-index" aria-hidden="true">01</div>
    </header>'''
competition_header = '''<header class="screen-hero compete-screen-hero vd4-masthead">
      <div class="screen-hero-copy"><div class="screen-kicker">LOCAL COMPETITION</div><div class="pause-title">COMPETE</div><div class="screen-subtitle">Race verified runs against their exact deterministic pace.</div></div>
      <div class="vd4-section-index" aria-hidden="true">02</div>
    </header>'''
mastery_header = '''<header class="screen-hero mastery-screen-hero vd4-masthead">
      <div class="screen-hero-copy"><div class="screen-kicker">SKILL BOOK</div><div class="pause-title">MASTERY</div><div class="screen-subtitle">Finite skill challenges. Visual rewards. No power upgrades.</div></div>
      <div class="vd4-section-index" aria-hidden="true">03</div>
    </header>'''

replace_regex(r'<header class="screen-hero records-screen-hero">.*?</header>', records_header, 'records masthead')
replace_regex(r'<header class="screen-hero compete-screen-hero">.*?</header>', competition_header, 'competition masthead')
replace_regex(r'<header class="screen-hero mastery-screen-hero">.*?</header>', mastery_header, 'mastery masthead')

replace_once('<span class="competition-rank">${i+1}</span>', '<span class="competition-rank">${String(i+1).padStart(2,\'0\')}</span>', 'competition rank format')
replace_once('NO RANKED RUNS YET', 'NO VERIFIED RUNS YET', 'competition empty copy')

CSS = r'''
/* === VD4 CUTFORM SECONDARY SCREENS ======================================= */
#recordsPanel,#competitionPanel,#masteryPanel{
  --vd4-rule:var(--vc-line-strong);
  --vd4-paper:var(--vc-surface);
  --vd4-paper-raised:var(--vc-surface-raised);
  --vd4-ink:var(--vc-ink);
  --vd4-muted:var(--vc-ink-muted);
  background:var(--vc-bg)!important;
  color:var(--vc-bg-ink)!important;
}
#recordsPanel::before,#competitionPanel::before,#masteryPanel::before{
  opacity:var(--vc-grain-opacity)!important;
  background-image:var(--vc-grain-image)!important;
  background-size:96px 96px!important;
  mask-image:none!important;
}
#recordsPanel .screen-nav,#competitionPanel .screen-nav,#masteryPanel .screen-nav{
  background:color-mix(in srgb,var(--vc-bg) 96%,transparent)!important;
  backdrop-filter:none!important;
  border-bottom:1px solid color-mix(in srgb,var(--vc-line) 70%,transparent)!important;
}
#recordsPanel .screen-nav .screen-back,#competitionPanel .screen-nav .screen-back,#masteryPanel .screen-nav .screen-back{
  min-height:42px!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;
  background:var(--vc-surface)!important;color:var(--vc-ink)!important;box-shadow:var(--vc-shadow-contact)!important;
}
#recordsPanel .screen-nav .screen-nav-brand,#competitionPanel .screen-nav .screen-nav-brand,#masteryPanel .screen-nav .screen-nav-brand{
  color:var(--vc-bg-ink-muted)!important;font-family:var(--vc-font-mono)!important;letter-spacing:.12em!important;
}
#recordsPanel .vd4-masthead,#competitionPanel .vd4-masthead,#masteryPanel .vd4-masthead{
  width:min(1180px,100%);margin:0 auto 30px!important;padding:28px 0 24px!important;min-height:150px!important;
  display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;align-items:end!important;gap:28px!important;
  border:0!important;border-bottom:4px solid var(--vc-line-strong)!important;border-radius:0!important;
  background:transparent!important;box-shadow:none!important;overflow:visible!important;
}
#recordsPanel .vd4-masthead::before,#recordsPanel .vd4-masthead::after,
#competitionPanel .vd4-masthead::before,#competitionPanel .vd4-masthead::after,
#masteryPanel .vd4-masthead::before,#masteryPanel .vd4-masthead::after{display:none!important}
#recordsPanel .screen-kicker,#competitionPanel .screen-kicker,#masteryPanel .screen-kicker{
  color:var(--vc-bg-ink-muted)!important;font:700 var(--vc-type-meta)/1 var(--vc-font-mono)!important;letter-spacing:.14em!important;
}
#recordsPanel .pause-title,#competitionPanel .pause-title,#masteryPanel .pause-title{
  color:var(--vc-bg-ink)!important;font:700 var(--vc-type-display)/.9 var(--vc-font-sans)!important;
  letter-spacing:var(--vc-track-display)!important;text-transform:uppercase!important;margin:8px 0 0!important;
}
#recordsPanel .screen-subtitle,#competitionPanel .screen-subtitle,#masteryPanel .screen-subtitle{
  max-width:650px!important;margin-top:12px!important;color:var(--vc-bg-ink-muted)!important;
  font:500 var(--vc-type-body)/1.4 var(--vc-font-sans)!important;letter-spacing:var(--vc-track-body)!important;
}
.vd4-section-index{
  align-self:end;color:var(--vc-accent);font:700 clamp(64px,8vw,112px)/.72 var(--vc-font-sans);
  letter-spacing:-.08em;font-variant-numeric:tabular-nums;user-select:none;
}
#competitionPanel .vd4-section-index{color:var(--vc-accent-alt)}
#masteryPanel .vd4-section-index{color:var(--vc-line-strong)}

/* Records — statistical archive / poster. */
#recordsPanel .records-scroll{width:min(1180px,100%);margin:0 auto!important;display:grid!important;grid-template-columns:repeat(12,minmax(0,1fr))!important;gap:28px 24px!important}
#recordsPanel .record-group{
  border:0!important;border-top:2px solid var(--vc-line-strong)!important;border-radius:0!important;
  padding:16px 0 0!important;background:transparent!important;box-shadow:none!important;color:var(--vc-ink)!important;
}
#recordsPanel .record-highlights{
  grid-column:1/-1!important;padding:24px!important;border:2px solid var(--vc-line-strong)!important;
  background:var(--vc-surface)!important;box-shadow:var(--vc-shadow-object)!important;
}
#recordsPanel .record-group:nth-child(2),#recordsPanel .record-group:nth-child(3){grid-column:span 6!important}
#recordsPanel .record-group:nth-child(4){grid-column:1/-1!important}
#recordsPanel .record-group-title{display:flex!important;align-items:baseline!important;justify-content:space-between!important;gap:16px!important;margin:0 0 16px!important}
#recordsPanel .record-group-title span{color:var(--vc-ink)!important;font:700 var(--vc-type-h3)/1 var(--vc-font-sans)!important;letter-spacing:-.02em!important}
#recordsPanel .record-group-title small{color:var(--vc-ink-muted)!important;font:500 var(--vc-type-meta)/1.2 var(--vc-font-sans)!important}
#recordsPanel .records-grid{gap:0!important}
#recordsPanel .record-card{
  min-height:112px!important;padding:18px!important;border:0!important;border-left:1px solid var(--vc-line)!important;border-radius:0!important;
  background:transparent!important;box-shadow:none!important;color:var(--vc-ink)!important;overflow:visible!important;
}
#recordsPanel .record-card:first-child{border-left:0!important}
#recordsPanel .record-card::before,#recordsPanel .record-card::after{display:none!important}
#recordsPanel .record-card.featured{
  min-height:150px!important;padding:20px!important;border-left:2px solid var(--vc-line-strong)!important;background:var(--vc-surface-raised)!important;
}
#recordsPanel .record-card.featured:first-child{border-left:0!important}
#recordsPanel .record-label{color:var(--vc-ink-muted)!important;font:700 var(--vc-type-meta)/1.2 var(--vc-font-mono)!important;letter-spacing:.08em!important}
#recordsPanel .record-value{margin-top:12px!important;color:var(--vc-ink)!important;font:700 clamp(28px,3.1vw,46px)/.92 var(--vc-font-sans)!important;letter-spacing:-.045em!important;font-variant-numeric:tabular-nums}
#recordsPanel .record-card.featured .record-value{font-size:clamp(38px,5vw,72px)!important}
#recordsPanel #watchBest,#recordsPanel .replay-actions,#recordsPanel .records-tech,#recordsPanel #recordsBack{width:min(720px,100%);margin-left:auto!important;margin-right:auto!important}
#recordsPanel .records-tech{border-radius:0!important;border-top:1px solid var(--vc-line)!important;background:transparent!important;box-shadow:none!important}

/* Competition — deterministic race sheet. */
#competitionPanel>.competition-target,#competitionPanel>#challengeBest,#competitionPanel>.competition-actions,
#competitionPanel>.competition-note,#competitionPanel>.competition-list-title,#competitionPanel>.competition-board,
#competitionPanel>.competition-tech,#competitionPanel>#competitionBack{width:min(980px,100%);margin-left:auto!important;margin-right:auto!important}
#competitionPanel .competition-target{
  position:relative!important;min-height:250px!important;padding:30px!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;
  background:var(--vc-surface)!important;box-shadow:var(--vc-shadow-object)!important;color:var(--vc-ink)!important;
  grid-template-columns:minmax(0,1fr) 92px minmax(0,1fr)!important;gap:22px!important;
}
#competitionPanel .competition-target::before{
  content:""!important;display:block!important;position:absolute!important;left:50%!important;top:22px!important;bottom:22px!important;width:2px!important;
  background:var(--vc-line)!important;transform:rotate(10deg)!important;pointer-events:none!important;
}
#competitionPanel .duel-side span{color:var(--vc-ink-muted)!important;font:700 var(--vc-type-meta)/1 var(--vc-font-mono)!important;letter-spacing:.10em!important}
#competitionPanel .duel-self>span{color:var(--vc-accent)!important}#competitionPanel .duel-target>span{color:var(--vc-accent-alt)!important}
#competitionPanel .duel-side strong{color:var(--vc-ink)!important;font:700 clamp(36px,5vw,66px)/.9 var(--vc-font-sans)!important;letter-spacing:-.055em!important;font-variant-numeric:tabular-nums}
#competitionPanel .duel-side small,#competitionPanel .competition-target-meta{color:var(--vc-ink-muted)!important;font-family:var(--vc-font-mono)!important}
#competitionPanel .duel-vs{gap:0!important}
#competitionPanel .duel-vs i{display:none!important}
#competitionPanel .duel-vs strong{
  width:52px!important;height:36px!important;display:grid!important;place-items:center!important;border:0!important;border-radius:0!important;
  background:var(--vc-line-strong)!important;color:var(--vc-surface)!important;box-shadow:none!important;font:700 13px/1 var(--vc-font-sans)!important;font-style:normal!important;
}
#competitionPanel .competition-target p{color:var(--vc-ink-muted)!important;font:500 var(--vc-type-small)/1.45 var(--vc-font-sans)!important}
#competitionPanel .competition-note{padding:14px 0!important;border:0!important;border-bottom:1px solid var(--vc-line)!important;border-radius:0!important;background:transparent!important;color:var(--vc-bg-ink-muted)!important;box-shadow:none!important;text-align:left!important}
#competitionPanel .competition-list-title{margin-top:34px!important;padding-bottom:10px!important;border-bottom:4px solid var(--vc-line-strong)!important;color:var(--vc-bg-ink)!important;font:700 var(--vc-type-h3)/1 var(--vc-font-sans)!important}
#competitionPanel .competition-list-title small{color:var(--vc-bg-ink-muted)!important;font-weight:500!important}
#competitionPanel .competition-board{border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface)!important;box-shadow:var(--vc-shadow-contact)!important;color:var(--vc-ink)!important;overflow:hidden!important}
#competitionPanel .competition-head{
  min-height:42px!important;background:var(--vc-line-strong)!important;color:var(--vc-on-substrate)!important;border:0!important;
  font:700 var(--vc-type-meta)/1 var(--vc-font-mono)!important;letter-spacing:.08em!important;
}
#competitionPanel .competition-row{min-height:66px!important;border-color:var(--vc-line)!important;background:transparent!important;color:var(--vc-ink)!important}
#competitionPanel .competition-row:nth-child(2){background:color-mix(in srgb,var(--vc-accent) 11%,var(--vc-surface))!important}
#competitionPanel .competition-row:nth-child(2)::before{content:"BEST";align-self:center;justify-self:start;padding:3px 5px;background:var(--vc-accent);color:var(--vc-on-accent);font:700 8px/1 var(--vc-font-mono);position:absolute;margin-left:44px;margin-top:-42px}
#competitionPanel .competition-rank{color:var(--vc-ink-muted)!important;font:700 20px/1 var(--vc-font-mono)!important;text-shadow:none!important}
#competitionPanel .competition-score{color:var(--vc-ink)!important;font:700 24px/1 var(--vc-font-sans)!important;letter-spacing:-.025em!important}
#competitionPanel .competition-ch,#competitionPanel .competition-time{color:var(--vc-ink-secondary)!important;font-family:var(--vc-font-mono)!important}
#competitionPanel .competition-tech{border-radius:0!important;background:transparent!important;box-shadow:none!important;border-top:1px solid var(--vc-line)!important}

/* Mastery — finite printed challenge book. */
#masteryPanel>#masteryHero,#masteryPanel>#masteryRewardTrack,#masteryPanel>#masteryTabs,#masteryPanel>#masteryChallenges,
#masteryPanel>.mastery-note-bottom,#masteryPanel>#masteryBack{width:min(1080px,100%);margin-left:auto!important;margin-right:auto!important}
#masteryPanel .mastery-hero{
  padding:26px!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-surface)!important;
  box-shadow:var(--vc-shadow-object)!important;color:var(--vc-ink)!important;
}
#masteryPanel .mastery-rank-emblem{
  width:84px!important;height:84px!important;border:2px solid var(--vc-line-strong)!important;border-radius:0!important;background:var(--vc-accent)!important;
  box-shadow:var(--vc-shadow-contact)!important;transform:rotate(45deg)!important;
}
#masteryPanel .mastery-rank-emblem::before,#masteryPanel .mastery-rank-emblem::after,#masteryPanel .mastery-rank-emblem span,#masteryPanel .mastery-rank-emblem i,#masteryPanel .mastery-rank-emblem b{display:none!important}
#masteryPanel .mastery-rank-kicker,#masteryPanel .mastery-mini-label{color:var(--vc-ink-muted)!important;font-family:var(--vc-font-mono)!important;letter-spacing:.08em!important}
#masteryPanel .mastery-rank{color:var(--vc-ink)!important;font:700 clamp(38px,5vw,64px)/.9 var(--vc-font-sans)!important;letter-spacing:-.05em!important}
#masteryPanel .mastery-points,#masteryPanel .mastery-summary-side,#masteryPanel .mastery-next{color:var(--vc-ink-secondary)!important}
#masteryPanel .mastery-points b,#masteryPanel .mastery-summary-side strong{color:var(--vc-ink)!important}
#masteryPanel .mastery-progress{height:12px!important;border:1px solid var(--vc-line-strong)!important;border-radius:0!important;background:transparent!important;overflow:hidden!important}
#masteryPanel .mastery-progress i{background:var(--vc-accent)!important;border-radius:0!important;box-shadow:none!important}
#masteryPanel .mastery-reward-track{display:grid!important;grid-template-columns:repeat(5,minmax(0,1fr))!important;gap:0!important;margin-top:26px!important;padding:0!important;border-top:4px solid var(--vc-line-strong)!important;overflow:visible!important}
#masteryPanel .mastery-reward{min-width:0!important;padding:14px 12px 10px!important;border:0!important;border-left:1px solid var(--vc-line)!important;border-radius:0!important;background:transparent!important;box-shadow:none!important;color:var(--vc-bg-ink-muted)!important}
#masteryPanel .mastery-reward:first-child{border-left:0!important}
#masteryPanel .mastery-reward.unlocked{color:var(--vc-bg-ink)!important;background:color-mix(in srgb,var(--vc-success) 7%,transparent)!important}
#masteryPanel .mastery-reward.current{box-shadow:inset 0 5px 0 var(--vc-accent)!important}
#masteryPanel .mastery-reward em{color:var(--vc-bg-ink-muted)!important;font-family:var(--vc-font-mono)!important}
#masteryPanel .mastery-reward b{color:currentColor!important;font-family:var(--vc-font-sans)!important}
#masteryPanel .mastery-reward span{color:currentColor!important;opacity:.72!important}
#masteryPanel .mastery-tabs{
  position:sticky!important;top:54px!important;z-index:12!important;display:flex!important;gap:0!important;margin-top:24px!important;padding:8px 0!important;
  border-top:1px solid var(--vc-line)!important;border-bottom:1px solid var(--vc-line)!important;background:color-mix(in srgb,var(--vc-bg) 96%,transparent)!important;backdrop-filter:none!important;
}
#masteryPanel .mastery-tab{
  min-height:42px!important;padding:0 16px!important;border:0!important;border-right:1px solid var(--vc-line)!important;border-radius:0!important;
  background:transparent!important;color:var(--vc-bg-ink-muted)!important;box-shadow:none!important;font:700 var(--vc-type-meta)/1 var(--vc-font-mono)!important;letter-spacing:.06em!important;
}
#masteryPanel .mastery-tab:last-child{border-right:0!important}
#masteryPanel .mastery-tab.active{background:var(--vc-line-strong)!important;color:var(--vc-on-substrate)!important}
#masteryPanel .mastery-overview-head{padding:20px 0 12px!important;border-bottom:4px solid var(--vc-line-strong)!important;color:var(--vc-bg-ink)!important}
#masteryPanel .mastery-overview-head strong{font:700 var(--vc-type-h3)/1 var(--vc-font-sans)!important}
#masteryPanel .mastery-overview-head span{color:var(--vc-bg-ink-muted)!important;font-family:var(--vc-font-mono)!important}
#masteryPanel .mastery-challenges{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:0!important}
#masteryPanel .mastery-card{
  position:relative!important;min-height:190px!important;padding:22px!important;border:0!important;border-bottom:1px solid var(--vc-line)!important;border-left:1px solid var(--vc-line)!important;border-radius:0!important;
  background:var(--vc-surface)!important;box-shadow:none!important;color:var(--vc-ink)!important;overflow:hidden!important;
}
#masteryPanel .mastery-card:nth-child(odd){border-left:0!important}
#masteryPanel .mastery-card::before{display:none!important}
#masteryPanel .mastery-card::after{content:""!important;display:none!important}
#masteryPanel .mastery-card.complete::after{
  content:"COMPLETE"!important;display:block!important;position:absolute!important;right:16px!important;top:17px!important;padding:5px 7px!important;
  border:2px solid var(--vc-success)!important;color:var(--vc-success)!important;background:var(--vc-surface)!important;font:700 9px/1 var(--vc-font-mono)!important;
  letter-spacing:.08em!important;transform:rotate(-2deg)!important;
}
#masteryPanel .mastery-card-cat,#masteryPanel .mastery-card-points{color:var(--vc-ink-muted)!important;font-family:var(--vc-font-mono)!important}
#masteryPanel .mastery-card h3{color:var(--vc-ink)!important;font:700 var(--vc-type-h3)/1.05 var(--vc-font-sans)!important;letter-spacing:-.02em!important;margin-top:16px!important}
#masteryPanel .mastery-card p{color:var(--vc-ink-secondary)!important;font:500 var(--vc-type-small)/1.45 var(--vc-font-sans)!important}
#masteryPanel .mastery-card-progress{color:var(--vc-ink-muted)!important;font-family:var(--vc-font-mono)!important}
#masteryPanel .mastery-card-progress b{color:var(--vc-ink)!important}
#masteryPanel .mastery-card-meter{height:8px!important;border:1px solid var(--vc-line-strong)!important;border-radius:0!important;background:transparent!important;overflow:hidden!important}
#masteryPanel .mastery-card-meter i{background:var(--vc-accent)!important;border-radius:0!important;box-shadow:none!important}
#masteryPanel .mastery-card.complete .mastery-card-meter i{background:var(--vc-success)!important}
#masteryPanel .mastery-note-bottom{margin-top:24px!important;padding:14px 0!important;border:0!important;border-top:1px solid var(--vc-line)!important;background:transparent!important;color:var(--vc-bg-ink-muted)!important;text-align:left!important}

@media(max-width:760px){
 #recordsPanel .vd4-masthead,#competitionPanel .vd4-masthead,#masteryPanel .vd4-masthead{min-height:118px!important;margin-bottom:20px!important;padding:20px 0 18px!important;gap:14px!important}
 .vd4-section-index{font-size:58px!important}
 #recordsPanel .records-scroll{grid-template-columns:1fr!important;gap:20px!important}
 #recordsPanel .record-group,#recordsPanel .record-group:nth-child(2),#recordsPanel .record-group:nth-child(3),#recordsPanel .record-group:nth-child(4){grid-column:1!important}
 #recordsPanel .record-highlights{padding:16px!important}.records-grid-featured{grid-template-columns:repeat(2,minmax(0,1fr))!important}
 #recordsPanel .record-card{min-height:96px!important;padding:14px!important}#recordsPanel .record-card.featured{min-height:120px!important}
 #competitionPanel .competition-target{grid-template-columns:1fr 52px 1fr!important;min-height:210px!important;padding:20px 16px!important;gap:10px!important}
 #competitionPanel .duel-side strong{font-size:32px!important}#competitionPanel .duel-vs strong{width:42px!important;height:32px!important}
 #competitionPanel .competition-target::before{top:16px!important;bottom:16px!important}
 #masteryPanel .mastery-hero{padding:18px!important}#masteryPanel .mastery-rank-emblem{width:62px!important;height:62px!important}
 #masteryPanel .mastery-reward-track{display:flex!important;overflow-x:auto!important;scroll-snap-type:x mandatory!important}
 #masteryPanel .mastery-reward{min-width:160px!important;scroll-snap-align:start!important}
 #masteryPanel .mastery-tabs{top:48px!important;overflow-x:auto!important}.mastery-tab{flex:0 0 auto!important}
 #masteryPanel .mastery-card{min-height:170px!important;padding:18px!important}
}
@media(max-width:480px){
 #recordsPanel .vd4-masthead,#competitionPanel .vd4-masthead,#masteryPanel .vd4-masthead{grid-template-columns:1fr auto!important;min-height:104px!important}.vd4-section-index{font-size:46px!important}
 #recordsPanel .pause-title,#competitionPanel .pause-title,#masteryPanel .pause-title{font-size:34px!important}
 #recordsPanel .screen-subtitle,#competitionPanel .screen-subtitle,#masteryPanel .screen-subtitle{font-size:12px!important}
 #recordsPanel .record-highlights{padding:12px!important}.records-grid-featured,.records-grid-compact,#recordsPanel .record-group:nth-child(4) .records-grid-compact{grid-template-columns:repeat(2,minmax(0,1fr))!important}
 #recordsPanel .record-value{font-size:22px!important}#recordsPanel .record-card.featured .record-value{font-size:30px!important}
 #competitionPanel .competition-target{grid-template-columns:1fr 38px 1fr!important;padding:16px 10px!important}.competition-target p{grid-column:1/-1!important}
 #competitionPanel .competition-head,#competitionPanel .competition-row{grid-template-columns:34px 1.3fr .8fr .85fr!important;padding:10px 8px!important;gap:4px!important}
 #competitionPanel .competition-score{font-size:18px!important}#competitionPanel .competition-rank{font-size:15px!important}
 #masteryPanel .mastery-challenges{grid-template-columns:1fr!important}#masteryPanel .mastery-card{border-left:0!important}
 #masteryPanel .mastery-card.complete::after{right:10px!important;top:11px!important;font-size:8px!important}
}
@media(orientation:landscape) and (min-width:760px) and (max-height:620px){
 #recordsPanel .vd4-masthead,#competitionPanel .vd4-masthead,#masteryPanel .vd4-masthead{min-height:72px!important;margin-bottom:10px!important;padding:8px 0!important;border-bottom-width:2px!important}.vd4-section-index{font-size:42px!important}
 #recordsPanel .screen-subtitle,#competitionPanel .screen-subtitle,#masteryPanel .screen-subtitle{display:none!important}
 #recordsPanel .records-scroll{gap:10px!important}#recordsPanel .record-group{padding-top:8px!important}#recordsPanel .record-card{min-height:68px!important;padding:9px!important}#recordsPanel .record-card.featured{min-height:82px!important}
 #competitionPanel .competition-target{min-height:126px!important;padding:12px 18px!important}.competition-target p{display:none!important}
 #masteryPanel .mastery-hero{padding:10px!important}#masteryPanel .mastery-rank-emblem{display:none!important}#masteryPanel .mastery-reward-track{margin-top:8px!important}#masteryPanel .mastery-tabs{top:40px!important;margin-top:8px!important;padding:4px 0!important}#masteryPanel .mastery-card{min-height:112px!important;padding:11px!important}
}
body.high-contrast #recordsPanel .record-highlights,body.high-contrast #competitionPanel .competition-target,body.high-contrast #competitionPanel .competition-board,body.high-contrast #masteryPanel .mastery-hero,body.high-contrast #masteryPanel .mastery-card{border-color:#fff!important;box-shadow:none!important}
body:has(.toggle[data-setting="reducedMotion"].is-on) #masteryPanel .mastery-card.complete::after{transform:none!important}
'''

if '/* === VD4 CUTFORM SECONDARY SCREENS' in text:
    raise SystemExit('VD4 CSS marker already exists unexpectedly')
replace_once('</style>', CSS + '\n</style>', 'VD4 CSS injection')

JS = r'''
// === VD4 SECONDARY SCREEN CONTRACT =========================================
const VD4_SECONDARY_VERSION='VD4.0.0';
function vd4SecondaryAudit(){
 const phase=document.querySelector('meta[name="voidcut-visual-phase"]')?.content||'';
 return Object.freeze({
  version:VD4_SECONDARY_VERSION,
  phase,
  recordsArchive:!!document.querySelector('#recordsPanel .vd4-section-index'),
  competitionRaceSheet:!!document.querySelector('#competitionPanel .vd4-section-index'),
  masteryChallengeBook:!!document.querySelector('#masteryPanel .vd4-section-index'),
  circularHeaderMarks:false,
  semanticThemeTokens:true,
  zeroPaddedRanks:true
 });
}
try{Object.defineProperty(window,'VoidcutSecondaryScreens',{value:Object.freeze({version:VD4_SECONDARY_VERSION,audit:vd4SecondaryAudit}),enumerable:true,configurable:true})}catch{window.VoidcutSecondaryScreens={version:VD4_SECONDARY_VERSION,audit:vd4SecondaryAudit}}
'''

replace_once('// === VD3 PRODUCT SHELL CONTRACT', JS + '\n\n// === VD3 PRODUCT SHELL CONTRACT', 'VD4 runtime contract')

INDEX.write_text(text, encoding='utf-8')
print('VD4 secondary screen patch applied')
print('HTML bytes:', len(text.encode('utf-8')))
