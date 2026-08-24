from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')


def exact(old, new, label, expected=1):
    global s
    n = s.count(old)
    if n != expected:
        raise SystemExit(f'{label}: expected {expected}, found {n}')
    s = s.replace(old, new)
    print(f'OK {label}: {n}')


def sub(pattern, repl, label, expected=1, flags=0):
    global s
    s2, n = re.subn(pattern, repl, s, count=expected, flags=flags)
    if n != expected:
        raise SystemExit(f'{label}: expected {expected}, found {n}')
    s = s2
    print(f'OK {label}: {n}')


# Current release contract no longer has a Daily subsystem.
exact('\n<meta name="voidcut-daily-generation" content="1">', '', 'daily meta')
exact(
    "const RELEASE_CONTRACT={save:16,replay:8,arena:2,director:6,daily:1};",
    "const RELEASE_CONTRACT={save:16,replay:8,arena:2,director:6};",
    'release contract',
)

# Remove the Daily menu surface.
sub(
    r'\n\s*<button id="daily" class="daily-run-card" aria-label="Start today\'s Daily Run">.*?</button>',
    '',
    'daily menu button',
    flags=re.S,
)

# Remove Daily persistence from the current normalized save model. Existing
# schema-16 saves still load: unknown legacy fields are ignored by normalizeSave.
sub(r'const defaultDaily=\(\)=>\(\{[^\n]*\}\);\n', '', 'default daily')
exact(',daily:defaultDaily()', '', 'daily default field')
sub(r'function normalizeDaily\(raw\)\{[^\n]*\}\n\n', '', 'normalize daily')
exact(',daily:normalizeDaily(source.daily)', '', 'daily normalized field')

# Remove Daily date/seed/streak/attempt helpers.
sub(
    r'function dailyKeyUTC\([^\n]*\nfunction previousDailyKey[^\n]*\nfunction dailySeedFor[^\n]*\nfunction dailyDateLabel[^\n]*\nfunction ensureDailyState[^\n]*\nfunction registerDailyStart[^\n]*\nfunction dailyBestReplay[^\n]*\n\n',
    '',
    'daily runtime helpers',
)

# Remove Daily run mode while preserving Standard and Duel/Challenge runs.
exact(',activeDailyKey=null', '', 'active daily state')
new_start = """function start(challenge=null,skipTutorial=false){screenCutTransition('cyan');if(!skipTutorial&&!challenge&&!save.tutorialSeen){startInteractiveTutorial('run');return}tutorialMode=false;tutorialLocked=false;clearTimeout(tutorialTimer);ui.tutorial.classList.remove('training');try{canvas.focus({preventScroll:true})}catch{try{canvas.focus()}catch{}}activeRunMode=challenge?'challenge':'standard';runCosmeticUnlocks=cosmeticUnlockCount(save);runCosmeticUnlockIds=new Set(cosmeticUnlockedEntries(save).map(x=>x.key));runMastery=newRunMastery();pendingMasteryUnlocks=[];if(challenge&&verifyCompetitiveReplay(challenge)){activeChallenge=JSON.parse(JSON.stringify(challenge));challengeAnalysis=analyzeReplayData(activeChallenge)}else{activeChallenge=null;challengeAnalysis=null}const seed=activeChallenge?.seed??freshSeed();sim.reset(seed,2,6);rebuildRenderGeometry();runRecord={version:8,arenaGeneration:2,directorGeneration:6,seed,events:[]};replayData=null;replayIndex=0;replayPaused=false;replaySpeed=1;replayAnalysis=null;lastCompletedReplay=null;transitionSerial++;state='play';paused=false;transition=false;aim=null;activePointerId=null;acc=0;last=performance.now();shownScore=0;scorePulse=0;shake=0;hudMultiplier=1;hudCombo=0;dangerPulse=0;deathImpact=0;visualHoldUntil=0;bounceState.clear();clearFx();hideAll();ui.replayHud.classList.add('hidden');ui.pauseBtn.style.display='block';ui.tutorial.classList.add('hidden');try{ensureAudioCtx();startAmbient();beepStart()}catch(err){captureIssue('audio-start',err)}}
"""
sub(
    r"function start\(challenge=null,skipTutorial=false,mode='standard'\)\{.*?\}\nfunction startDaily\(skipTutorial=false\)\{.*?\}\n(?=function tutorialArena)",
    new_start,
    'daily run mode',
    flags=re.S,
)
exact("else if(ret==='daily')startDaily(true);", '', 'daily tutorial return')

# Remove Daily menu rendering.
sub(r"const daily=ensureDailyState\(\);.*?;const mp=", 'const mp=', 'daily menu renderer')

# Remove Daily labels and Daily result handling.
exact(
    "function vd2ModeName(){return activeRunMode==='daily'?'DAILY':activeRunMode==='challenge'?'DUEL':state==='replay'?'REPLAY':'STANDARD'}",
    "function vd2ModeName(){return activeRunMode==='challenge'?'DUEL':state==='replay'?'REPLAY':'STANDARD'}",
    'mode label',
)
new_showcase = "function setResultShowcase({verified=false,records=[],unlocks=0,duel=''}={}){const gradeEl=$('resultGrade'),labelEl=$('resultGradeLabel'),rewards=$('resultRewards');if(!gradeEl||!labelEl||!rewards)return;let grade,label;if(verified){grade='✓';label='DETERMINISTIC MATCH'}else [grade,label]=resultGradeForRun();gradeEl.textContent=grade;gradeEl.dataset.grade=grade;labelEl.textContent=label;const chips=[];if(duel)chips.push(`<span class=\"result-reward-chip duel\">${escapeHtml(duel)}</span>`);for(const r of (records||[]).slice(0,4))chips.push(`<span class=\"result-reward-chip record\">${escapeHtml(r)}</span>`);if(unlocks)chips.push(`<span class=\"result-reward-chip unlock\">${unlocks} STYLE${unlocks===1?'':'S'} UNLOCKED</span>`);if(verified)chips.push('<span class=\"result-reward-chip record\">REPLAY VERIFIED</span>');rewards.innerHTML=chips.join('')}"
sub(r'function setResultShowcase\([^\n]*', new_showcase, 'daily result showcase')
sub(
    r"\nif\(activeRunMode==='daily'\)\{[^\n]*\}\n(?=const best=)",
    '\n',
    'daily result branch',
)

# Remove now-unused Daily presentation state toggles from runtime.
s = s.replace("ui.challengeHud.classList.remove('daily-mode');", '')
s = s.replace("ui.result.classList.remove('daily-result');", '')

# Diagnostics certify only live product contracts.
sub(r'\nfunction activeDailyDiagnosticState\(\)\{[^\n]*\}', '', 'daily diagnostic state')
meta_probe = ",daily:+(document.querySelector('meta[name=\"voidcut-daily-generation\"]')?.content||NaN)"
exact(meta_probe, '', 'daily diagnostic metadata', expected=2)
exact('||releaseMetaAudit.daily!==RELEASE_CONTRACT.daily', '', 'stress daily contract comparison')
exact('&&releaseMeta.daily===RELEASE_CONTRACT.daily', '', 'system daily contract comparison')
exact("'menu','play','daily','records'", "'menu','play','records'", 'required daily UI')
sub(
    r"const dkA='2031-02-03',dkB='2031-02-04';if\(dailySeedFor\(dkA\)!==dailySeedFor\(dkA\)\|\|dailySeedFor\(dkA\)===dailySeedFor\(dkB\)\)failures.push\('Daily seed stability/separation contract failed.'\);",
    '',
    'daily stress seed contract',
)
exact(',`Daily seed contract PASS`', '', 'daily stress note')
sub(
    r"const dates=new Set;for\(let i=0;i<128;i\+\+\)\{const d=new Date\(Date.UTC\(2026,0,1\+i\)\),key=d.toISOString\(\).slice\(0,10\),seed=dailySeedFor\(key\)>>>0;if\(dates.has\(seed\)\)failures.push\(`Daily seed collision detected near \$\{key\}\.`\);dates.add\(seed\)\}",
    '',
    'daily collision audit',
)
exact(",'128 daily seeds'", '', 'daily audit summary')
exact(
    'const dd=activeDailyDiagnosticState();if(dd.bestReplay&&(!validReplay(dd.bestReplay)||dd.bestReplay.seed!==(dailySeedFor(dd.date)>>>0)||!verifyCompetitiveReplay(dd.bestReplay)))failures.push("Daily best replay is invalid, mismatched, or fails deterministic verification.");',
    '',
    'daily system replay validation',
)
exact(' • DAILY ${RELEASE_CONTRACT.daily}', '', 'daily ruleset diagnostic')
sub(
    r",`DAILY: \$\{dd\.date\}.*?(?=,`PRESENTATION:)",
    '',
    'daily diagnostic line',
)

# No control can route into Daily anymore.
exact("$('play').onclick=()=>start();$('daily').onclick=()=>startDaily();", "$('play').onclick=()=>start();", 'daily click handler')
sub(
    r"\$\('retry'\)\.onclick=\(\)=>\{if\(activeRunMode==='daily'\)startDaily\(true\);else\{\$\('retry'\)\.textContent='RETRY';const target=activeChallenge;start\(target\)\}\};",
    "$('retry').onclick=()=>{$('retry').textContent='RETRY';const target=activeChallenge;start(target)};",
    'daily retry route',
)
exact(
    "$('restart').onclick=()=>tutorialMode?startInteractiveTutorial(tutorialReturn):activeRunMode==='daily'?startDaily(true):start(activeChallenge);",
    "$('restart').onclick=()=>tutorialMode?startInteractiveTutorial(tutorialReturn):start(activeChallenge);",
    'daily restart route',
)
sub(
    r"\$\('copyRun'\)\.onclick=\(\)=>activeRunMode==='daily'\?copyChallengeCode\(lastCompletedReplay\|\|dailyBestReplay\(\)\):copyReplayCode\(lastCompletedReplay\|\|replayData\|\|save.bestReplay\);",
    "$('copyRun').onclick=()=>copyReplayCode(lastCompletedReplay||replayData||save.bestReplay);",
    'daily share route',
)

# Competitive HUD and mastery/progression no longer special-case Daily.
new_hud = "function updateChallengeHud(){ui.challengeHud.classList.add('hidden');vd2CompetitiveStatus={kind:'',text:'',tone:'neutral'};if(state!=='play'||!activeChallenge||!challengeAnalysis)return;const target=competitivePaceAt(challengeAnalysis,sim.runElapsed),delta=sim.score-target.score,sign=delta>0?'+':'';vd2CompetitiveStatus={kind:'duel',text:`DUEL ${sign}${delta.toLocaleString()} / YOU ${sim.score.toLocaleString()} / PACE ${target.score.toLocaleString()} / CH ${sim.chamber}:${target.chamber}`,tone:delta>=0?'accent':'danger'}}"
sub(r'function updateChallengeHud\(\)\{[^\n]*', new_hud, 'daily competitive HUD')
exact(
    "if(state==='play'&&!tutorialMode&&activeRunMode!=='daily')progressionOnResolution(r.res);",
    "if(state==='play'&&!tutorialMode)progressionOnResolution(r.res);",
    'daily progression exclusion',
)

# Remove Daily from public VD6/VD7 audit contracts.
exact(',daily:RELEASE_CONTRACT.daily', '', 'public daily audit contracts', expected=2)

# Product removal gate: Daily may remain only in orphaned CSS declarations above
# </style>; no HTML or JavaScript route/state/label is allowed to survive.
style_end = s.index('</style>')
live = s[style_end:]
leftovers = list(re.finditer(r'daily', live, re.I))
if leftovers:
    contexts = []
    for m in leftovers[:30]:
        a = max(0, m.start() - 80)
        b = min(len(live), m.end() + 120)
        contexts.append(live[a:b].replace('\n', ' '))
    raise SystemExit('Live Daily references remain:\n' + '\n---\n'.join(contexts))

path.write_text(s, encoding='utf-8')
print(f'WROTE index.html: {len(s)} chars')

# Force installed PWAs to pick up the new shell.
sw = Path('sw.js')
sw_text = sw.read_text(encoding='utf-8')
old = "const VOIDCUT_CACHE_VERSION = '6.0.0-pwa4';"
new = "const VOIDCUT_CACHE_VERSION = '6.0.0-pwa5';"
if sw_text.count(old) != 1:
    raise SystemExit(f'Unexpected service-worker cache version; expected exactly one {old!r}')
sw.write_text(sw_text.replace(old, new), encoding='utf-8')
print('WROTE sw.js: pwa5')
