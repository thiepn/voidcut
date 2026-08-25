import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve('..');
const indexPath = path.join(root, 'index.html');
const swPath = path.join(root, 'sw.js');
const clientPath = path.resolve('client/global-leaderboard-runtime.js');
let s = fs.readFileSync(indexPath, 'utf8');
let sw = fs.readFileSync(swPath, 'utf8');
const client = fs.readFileSync(clientPath, 'utf8').trim();

function once(oldText, newText, label = oldText.slice(0, 80)) {
  const count = s.split(oldText).length - 1;
  if (count !== 1) throw new Error(`Expected exactly one ${label}; found ${count}`);
  s = s.replace(oldText, newText);
}
function regexOnce(re, replacement, label) {
  const matches = [...s.matchAll(new RegExp(re.source, re.flags.includes('g') ? re.flags : re.flags + 'g'))];
  if (matches.length !== 1) throw new Error(`Expected exactly one ${label}; found ${matches.length}`);
  s = s.replace(re, replacement);
}

// Release contracts.
once('<meta name="voidcut-build" content="6.0.0">','<meta name="voidcut-build" content="6.1.0">','build meta');
once('<meta name="voidcut-save-schema" content="16">','<meta name="voidcut-save-schema" content="17">','save meta');
once('<meta name="voidcut-replay-version" content="8">','<meta name="voidcut-replay-version" content="9">','replay meta');
once("const RELEASE_VERSION='6.0.0',RELEASE_CHANNEL='STABLE',BUILD_ID='6.0.0',RELEASE_NAME='VISUAL RELEASE';const RELEASE_CONTRACT={save:16,replay:8,arena:2,director:6};", "const RELEASE_VERSION='6.1.0',RELEASE_CHANNEL='STABLE',BUILD_ID='6.1.0',RELEASE_NAME='GLOBAL COMPETITION';const RELEASE_CONTRACT={save:17,replay:9,arena:2,director:6};", 'release constants');
once("const SAVE_SCHEMA=16,SAVE_KEY=", "const SAVE_SCHEMA=17,SAVE_KEY=", 'save schema constant');
s = s.replaceAll('VERSION 6.0.0', 'VERSION 6.1.0');
s = s.replaceAll('VOIDCUT 6.0.0 RELEASE AUDIT', 'VOIDCUT 6.1.0 GLOBAL COMPETITION AUDIT');

// Grade bonus: additive and depth-scaled. Legacy replay scoring is preserved by scoringVersion.
once("function efficiencyBonus(chamber,cuts){if(cuts<=3)return 7500*chamber;if(cuts===4)return 4500*chamber;if(cuts===5)return 2500*chamber;if(cuts===6)return 1000*chamber;return 0}", "function efficiencyBonus(chamber,cuts){if(cuts<=3)return 7500*chamber;if(cuts===4)return 4500*chamber;if(cuts===5)return 2500*chamber;if(cuts===6)return 1000*chamber;return 0}\nfunction gradeBonus(chamber,grade){const unit={'S+':12000,S:8000,A:5000,B:2500,C:1000,D:0}[grade]||0;return unit*Math.max(1,chamber|0)}", 'efficiency bonus function');
once("reset(seed=freshSeed(),arenaGen=2,directorGen=6){this.arenaGen=arenaGen;this.directorGen=directorGen;", "reset(seed=freshSeed(),arenaGen=2,directorGen=6,scoringVersion=9){this.arenaGen=arenaGen;this.directorGen=directorGen;this.scoringVersion=scoringVersion;", 'Sim reset signature');
once("const empty=()=>({removed:0,gain:0,baseGain:0,completionBonus:0,efficiencyBonus:0,pct:0,complete:false", "const empty=()=>({removed:0,gain:0,baseGain:0,completionBonus:0,efficiencyBonus:0,gradeBonus:0,pct:0,complete:false", 'empty resolution result');
once("this.plan.pressure):null;if(complete){", "this.plan.pressure):null,rankBonus=complete&&this.scoringVersion>=9?gradeBonus(this.chamber,mastery?.grade):0;if(complete){", 'rank bonus calculation');
once("this.masteryBonus+=Math.max(0,gain-baseGain)+effBonus;this.score+=gain+completionBonus+effBonus;return{removed,gain,baseGain,completionBonus,milestoneBonus,efficiencyBonus:effBonus,pct", "this.masteryBonus+=Math.max(0,gain-baseGain)+effBonus+rankBonus;this.score+=gain+completionBonus+effBonus+rankBonus;return{removed,gain,baseGain,completionBonus,milestoneBonus,efficiencyBonus:effBonus,gradeBonus:rankBonus,pct", 'score accumulation');

// Replay v9 and ruleset-aware legacy playback.
once("||(r.version===8&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6);if(!supported)", "||(r.version===8&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6)||(r.version===9&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6);if(!supported)", 'v9 replay validation');
once("function replayRulesetLabel(r){const a=replayArenaGeneration(r),d=replayDirectorGeneration(r);if(r.version===8&&a===2&&d===6)return'CURRENT • REPLAY v8 • ARENA 2 • DIRECTOR 6';", "function replayRulesetLabel(r){const a=replayArenaGeneration(r),d=replayDirectorGeneration(r);if(r.version===9&&a===2&&d===6)return'CURRENT • REPLAY v9 • ARENA 2 • DIRECTOR 6';if(r.version===8&&a===2&&d===6)return'LEGACY v6.0 • REPLAY v8 • DIRECTOR 6';", 'replay ruleset label');
once("function replayDirectorGeneration(r){return r?.version>=7?(r.directorGeneration||6):r?.version===6?", "function replayDirectorGeneration(r){return r?.version>=7?(r.directorGeneration||6):r?.version===6?", 'director generation anchor');
once("function replayExportCode(r){", "function replayScoringVersion(r){return r?.version>=9?9:8}\nfunction replayExportCode(r){", 'replay scoring version');
once("s.reset(data.seed,replayArenaGeneration(data),replayDirectorGeneration(data));", "s.reset(data.seed,replayArenaGeneration(data),replayDirectorGeneration(data),replayScoringVersion(data));", 'analysis scoring version');
once("s.reset(replayData.seed,replayArenaGeneration(replayData),replayDirectorGeneration(replayData));", "s.reset(replayData.seed,replayArenaGeneration(replayData),replayDirectorGeneration(replayData),replayScoringVersion(replayData));", 'seek scoring version');
// startReplay has a direct sim.reset call distinct from seekReplay.
once("sim.reset(replayData.seed,replayArenaGeneration(replayData),replayDirectorGeneration(replayData));rebuildRenderGeometry();state='replay';", "sim.reset(replayData.seed,replayArenaGeneration(replayData),replayDirectorGeneration(replayData),replayScoringVersion(replayData));rebuildRenderGeometry();state='replay';", 'startReplay scoring version');
once("function competitiveEligible(r){return validReplay(r)&&(r.version===7||r.version===8)&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6}", "function competitiveEligible(r){return validReplay(r)&&(r.version===7||r.version===8||r.version===9)&&(r.arenaGeneration||2)===2&&(r.directorGeneration||6)===6}", 'competitive eligibility');
once("const r={version:8,arenaGeneration:2,directorGeneration:6,seed:runRecord.seed>>>0", "const r={version:9,arenaGeneration:2,directorGeneration:6,seed:runRecord.seed>>>0", 'finished replay version');

// Inject the global leaderboard client after the legacy local competition helpers.
once("function competitivePaceAt(a,time){", `${client}\n\nfunction competitivePaceAt(a,time){`, 'leaderboard runtime insertion');

// Ranked main run uses a prefetched server ticket and server-issued seed. Offline fallback remains unchanged.
once("const seed=activeChallenge?.seed??freshSeed();sim.reset(seed,2,6);rebuildRenderGeometry();runRecord={version:8,arenaGeneration:2,directorGeneration:6,seed,events:[]};", "const rankTicket=!challenge?takeLeaderboardTicket():null,seed=activeChallenge?.seed??rankTicket?.seed??freshSeed();activeLeaderboardTicket=!challenge&&rankTicket&&rankTicket.seed===seed?rankTicket:null;void prefetchLeaderboardTicket();sim.reset(seed,2,6,9);rebuildRenderGeometry();runRecord={version:9,arenaGeneration:2,directorGeneration:6,seed,events:[]};", 'ranked run start');
once("function showMenu(){\nscreenCutTransition('cyan');", "function showMenu(){\nscreenCutTransition('cyan');void prefetchLeaderboardTicket();", 'menu ticket prefetch');

// Submit the completed main run globally; retire local leaderboard writes/ranks.
once("const completed=finishRunRecord();lastCompletedReplay=completed;", "const completed=finishRunRecord();lastCompletedReplay=completed;const leaderboardTicketForRun=activeLeaderboardTicket;activeLeaderboardTicket=null;if(completed&&leaderboardTicketForRun)queueLeaderboardSubmission(completed,leaderboardTicketForRun);", 'run completion global submit');
once("const competitionRank=completed?addCompetitiveRun(completed):null;persist();", "const competitionRank=null;persist();", 'retire local rank write');

// Global competition screen: one board, main PLAY only.
regexOnce(/function showCompetition\(\)\{[\s\S]*?\}\n\nfunction renderMastery\(\)\{/, `function showCompetition(){screenCutTransition('magenta');hideAll();ui.replayHud.classList.add('hidden');const board=$('competitionBoard');board.innerHTML='<div class="competition-row competition-empty"><span>LOADING GLOBAL LEADERBOARD…</span></div>';$('competitionNote').textContent='SERVER-VERIFIED MAIN RUNS • REPLAY v9';ui.competition.scrollTop=0;ui.competition.classList.remove('hidden');state='competition';void loadGlobalLeaderboard()}\n\nfunction renderMastery(){`, 'showCompetition function');
once('<div class="screen-kicker">LOCAL COMPETITION</div><div class="pause-title">COMPETE</div><div class="screen-subtitle">Race verified runs against their exact deterministic pace.</div>', '<div class="screen-kicker">GLOBAL COMPETITION</div><div class="pause-title">GLOBAL LEADERBOARD</div><div class="screen-subtitle">One worldwide ranking for the canonical PLAY run. Every published score is replay-verified.</div>', 'competition masthead');
once('<span class="tile-label">COMPETE</span><span class="tile-sub">Device leaderboard and challenge imports</span>', '<span class="tile-label">LEADERBOARD</span><span class="tile-sub">Global ranking • replay verified</span>', 'menu leaderboard tile');
once('LOCAL LEADERBOARD <small>Top verified runs saved on this device</small>', 'GLOBAL LEADERBOARD <small>Top 100 verified main-run scores</small>', 'leaderboard title');
once('New competitive runs are checked by replaying their inputs locally before they enter this board. This protects the local rankings without changing gameplay.', 'Global scores use server-issued run tickets and are accepted only after deterministic replay verification. Only the canonical PLAY run is ranked.', 'competition tech copy');
s = s.replaceAll('CURRENT RULESET • REPLAY v8 • ARENA 2 • DIRECTOR 6', 'CURRENT RULESET • REPLAY v9 • ARENA 2 • DIRECTOR 6');

// Explain the actual scoring model in tutorial copy.
once('Removed area earns points. Bigger cuts and close calls multiply them; clearing adds a chamber bonus, and fewer cuts add an efficiency bonus. Dividers are setup tools and score 0.', 'Removed area earns points. Bigger cuts and close calls multiply them; clearing adds chamber and efficiency bonuses. D–S+ chamber grades add increasingly large bonuses that scale with chamber depth. Dividers are setup tools and score 0.', 'tutorial scoring text');
once('Removed area earns points. Bigger cuts and close calls multiply points. Chamber clears and fewer cuts add bonuses. Dividers score zero.', 'Removed area earns points. Bigger cuts and close calls multiply points. Chamber clears, efficiency and higher D through S plus grades add depth-scaled bonuses. Dividers score zero.', 'tutorial scoring announcement');

// Retire visible legacy duel/challenge controls and style the global board/profile prompt.
const css = `\n/* VOIDCUT v6.1 — global leaderboard */\n#competitionTarget,#challengeBest,#copyChallenge,#importChallenge,#copySubmission,#watchCompetitionBest{display:none!important}\n#competitionPanel>.competition-actions{display:none!important}\n#competitionPanel .competition-head,#competitionPanel .competition-row{grid-template-columns:64px minmax(120px,1fr) minmax(120px,1.1fr) 90px!important}\n#competitionPanel .leaderboard-row{width:100%;border:0;border-top:1px solid var(--vc-line)!important;border-radius:0!important;text-align:left;cursor:pointer}\n#competitionPanel .leaderboard-row.is-self{box-shadow:inset 5px 0 0 var(--vc-accent-alt)!important}\n#competitionPanel .leaderboard-name{font:700 15px/1.1 var(--vc-font-sans);color:var(--vc-ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.leaderboard-join{width:min(620px,92vw);padding:15px 16px;margin:2px 0 4px;border:1px solid var(--vc-line-strong);background:var(--vc-surface);color:var(--vc-ink);text-align:left}\n.leaderboard-join-copy{display:flex;flex-direction:column;gap:3px}.leaderboard-join-copy strong{font:800 14px var(--vc-font-sans);letter-spacing:.06em}.leaderboard-join-copy span,.leaderboard-join-status{font:600 10px var(--vc-font-mono);color:var(--vc-ink-muted)}\n.leaderboard-join-form{display:grid;grid-template-columns:1fr 112px;gap:8px;margin-top:10px}.leaderboard-join-form input{min-height:46px;padding:0 12px;border:1px solid var(--vc-line-strong);background:var(--vc-bg);color:var(--vc-bg-ink);font:700 14px var(--vc-font-mono);text-transform:uppercase}.leaderboard-join-form button{min-height:46px}.leaderboard-join-status{min-height:14px;margin-top:7px}\n@media(max-width:480px){#competitionPanel .competition-head,#competitionPanel .competition-row{grid-template-columns:38px minmax(86px,1fr) minmax(88px,1fr) 58px!important}.leaderboard-join-form{grid-template-columns:1fr}.leaderboard-join-form button{width:100%}}\n`;
once('\n</style>\n\n<link rel="stylesheet" href="./design/voidcut-design-system.css" />', `${css}\n</style>\n\n<link rel="stylesheet" href="./design/voidcut-design-system.css" />`, 'global leaderboard CSS');

// Diagnostics/build strings that are expected to track the current replay contract.
s = s.replaceAll('CURRENT REPLAY v8', 'CURRENT REPLAY v9');
s = s.replaceAll('version:8,arenaGeneration:2,directorGeneration:6', 'version:9,arenaGeneration:2,directorGeneration:6');

// PWA cache revision.
const oldCache = "const VOIDCUT_CACHE_VERSION = '6.0.0-pwa5';";
if (!sw.includes(oldCache)) throw new Error('Expected current service-worker cache revision');
sw = sw.replace(oldCache, "const VOIDCUT_CACHE_VERSION = '6.1.0-pwa1';");

// Contract checks before write.
for (const marker of [
  "RELEASE_VERSION='6.1.0'",
  'const SAVE_SCHEMA=17',
  'function gradeBonus(chamber,grade)',
  'rankBonus=complete&&this.scoringVersion>=9',
  "version:9,arenaGeneration:2,directorGeneration:6",
  "const LEADERBOARD_API='https://voidcut-api.thiepn.dev'",
  "function replayScoringVersion(r){return r?.version>=9?9:8}",
  'GLOBAL LEADERBOARD',
]) if (!s.includes(marker)) throw new Error(`Missing expected v6.1 marker: ${marker}`);

fs.writeFileSync(indexPath, s);
fs.writeFileSync(swPath, sw);
console.log('VOIDCUT v6.1 game patch applied.');
