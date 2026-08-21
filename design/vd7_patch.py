from pathlib import Path

INDEX = Path('index.html')
CSS = Path('design/voidcut-design-system.css')

index = INDEX.read_text(encoding='utf-8')
css = CSS.read_text(encoding='utf-8')

if '/* === VD7 THEME SUITE + RESPONSIVE CERTIFICATION' in index:
    print('VD7 already applied')
    raise SystemExit(0)

# Semantic contrast corrections. These are deliberately token-level so every
# reconstructed surface receives the fix without component-specific patches.
replacements = {
    '--vc-bg-ink-muted: #6A675F;': '--vc-bg-ink-muted: #66625A;',
    '--vc-ink-muted: #7C786F;': '--vc-ink-muted: #726E66;',
    '--vc-on-accent: #FFF9ED;': '--vc-on-accent: #171714;',
    '--vc-ink-muted: #77736A;': '--vc-ink-muted: #6D695F;',
    '--vc-ink-secondary: #5D6A61;': '--vc-ink-secondary: #56645B;',
    '--vc-ink-muted: #768077;': '--vc-ink-muted: #5B655D;',
    '--vc-ink-secondary: #745D6E;': '--vc-ink-secondary: #695269;',
    '--vc-ink-muted: #8E7688;': '--vc-ink-muted: #71576B;',
    '--vc-on-accent: #FFF1E7;': '--vc-on-accent: #241620;',
}
for old, new in replacements.items():
    if old not in css:
        raise SystemExit(f'Missing design token to certify: {old}')
    css = css.replace(old, new)

index = index.replace('<meta name="voidcut-visual-phase" content="VD6">', '<meta name="voidcut-visual-phase" content="VD7">', 1)
if '<meta name="voidcut-visual-phase" content="VD7">' not in index:
    raise SystemExit('Could not advance visual phase to VD7')

vd7_css = r'''

/* === VD7 THEME SUITE + RESPONSIVE CERTIFICATION ========================== */
/* Final ownership layer. Historical v5 variables remain for compatibility,
   but visible product color resolves through the semantic CUTFORM system. */
:root{
  --bg:var(--vc-bg);
  --bg-deep:var(--vc-substrate);
  --surface:var(--vc-surface);
  --surface-2:var(--vc-surface-raised);
  --surface-3:var(--vc-surface-raised);
  --line:var(--vc-line);
  --line-strong:var(--vc-line-strong);
  --text:var(--vc-ink);
  --text-2:var(--vc-ink-secondary);
  --muted:var(--vc-ink-muted);
  --cyan:var(--vc-accent);
  --cyan-soft:color-mix(in srgb,var(--vc-accent) 16%,transparent);
  --magenta:var(--vc-accent-alt);
  --magenta-soft:color-mix(in srgb,var(--vc-accent-alt) 15%,transparent);
  --danger:var(--vc-danger);
  --warning:var(--vc-accent-alt);
  --display:var(--vc-font-sans);
  --body:var(--vc-font-sans);
  --mono:var(--vc-font-mono);
  --r-sm:var(--vc-radius-1);
  --r-md:var(--vc-radius-2);
  --r-lg:var(--vc-radius-2);
}
html,body{background:var(--vc-bg)!important;color:var(--vc-bg-ink)!important;font-family:var(--vc-font-sans)!important}
body{background:var(--vc-bg)!important}
button,input{font-family:inherit}
button:focus-visible,input:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--vc-focus)!important;outline-offset:3px!important}
#wrap{background:var(--vc-substrate)!important;box-shadow:none!important}
#wrap::before,#wrap::after{display:none!important}
.overlay{background:var(--vc-bg)!important;color:var(--vc-bg-ink)!important;overflow-x:hidden!important;max-width:100vw!important}
.overlay::before{opacity:var(--vc-grain-opacity)!important;background-image:var(--vc-grain-image)!important;background-size:96px 96px!important;mask-image:none!important}
.overlay::after{display:none!important}
.vc-screen-cut,.vc-screen-cut[data-tone="cyan"],.vc-screen-cut[data-tone="magenta"]{--cut-a:var(--vc-accent)!important;--cut-b:var(--vc-accent-alt)!important}
[data-vc-icon].primary::before{filter:none!important}
#menu .logo-cyan{color:var(--vc-bg-ink)!important;filter:none!important}
#menu .logo-magenta{color:var(--vc-accent)!important;filter:none!important}
#menu .menu-tagline,#menu .version,#menu .primary-sub,#menu .tile-sub,#menu .hint{color:var(--vc-bg-ink-muted)!important}
#menu .menu-tagline span,#menu .daily-kicker,#menu .best-subline{color:var(--vc-accent)!important}
#menu .menu-status-caption{color:var(--vc-bg-ink-muted)!important}
#menu .health-note{color:var(--vc-danger)!important}
.orientation-notice,#orientationNotice{inset:0!important;width:100vw!important;height:100dvh!important;margin:0!important;border:0!important;box-shadow:none!important;background:var(--vc-bg)!important;color:var(--vc-bg-ink)!important}
.orientation-notice span{color:var(--vc-bg-ink-muted)!important}
.screen-nav .screen-back,.cos-back,#settingsPanel .toggle,.mastery-tab,.cos-cat-tab,.replay-controls button,.replay-highlights button,.replay-exit{min-height:44px!important}
#settingsPanel .toggle{height:auto!important}
.vd6-replay-instrument .replay-highlights button,.vd6-replay-instrument .replay-exit{min-height:44px!important}
.short-swipe{max-width:min(260px,calc(100vw - 24px));overflow-wrap:anywhere}
.overlay button,.overlay [role="button"],.overlay summary{touch-action:manipulation}
.overlay h1,.overlay h2,.overlay h3,.overlay p,.overlay small,.overlay span,.setting-copy,.record-value,.competition-row,.mastery-card,.cos-card{min-width:0;overflow-wrap:anywhere}
#recordsPanel,#competitionPanel,#masteryPanel,#cosmeticsPanel,#settingsPanel,#diagnosticsPanel{overflow-x:hidden!important}
.vd6-report-sheet,.vd6-replay-instrument,.pause-shell,.result-shell,.cos-hero,.menu-stage{max-width:100%!important}

/* Phone certification: vertical scroll is allowed, horizontal drift is not. */
@media(max-width:480px){
  .overlay{padding-left:max(12px,env(safe-area-inset-left))!important;padding-right:max(12px,env(safe-area-inset-right))!important}
  .screen-nav .screen-back,.cos-back,#settingsPanel .toggle,.mastery-tab,.cos-cat-tab,.vd6-replay-instrument .replay-highlights button,.vd6-replay-instrument .replay-controls button,.vd6-replay-instrument .replay-exit{min-height:44px!important}
  .vd6-replay-instrument .replay-highlights{grid-template-columns:repeat(3,minmax(0,1fr))!important;width:100%!important}
  .vd6-replay-instrument .replay-highlights button{padding:0 4px!important;font-size:8px!important}
  .vd6-replay-actions{grid-template-columns:1fr!important}
  .vd6-replay-instrument .replay-exit{border-left:0!important;border-top:2px solid var(--vc-danger)!important}
  .settings-actions,.result-actions,.pause-actions-secondary{min-width:0!important}
}

/* Short desktop/landscape is a dedicated composition, not a scaled tall page. */
@media(min-width:1000px) and (max-height:780px){
  #menu{grid-template-columns:minmax(300px,420px) minmax(420px,600px)!important;grid-template-rows:auto auto auto auto auto auto!important;gap:7px 28px!important;padding:14px 28px!important;align-content:center!important}
  #menu>.menu-topbar{min-height:42px!important}.logo-lockup{font-size:58px!important;margin:0!important}.menu-tagline{font-size:10px!important;margin:0!important}
  .menu-stage{min-height:340px!important;max-height:420px!important}.hero-art-label{bottom:14px!important}.hero-art-label strong{font-size:19px!important}.hero-art-label em{display:none!important}
  #best{padding:4px 0!important}.best-value{font-size:27px!important}#play{height:62px!important}.primary-text{font-size:27px!important}.daily-run-card{min-height:56px!important;padding-block:9px!important}
  .menu-grid{gap:8px!important}.menu-tile{min-height:54px!important;padding:9px 12px!important}.tile-sub{display:none!important}#menu .hint{display:none!important}
  .result-shell{min-height:100dvh!important;padding:18px 0!important}.result-score-stage{min-height:220px!important}.result-score{font-size:68px!important}
}

/* Tablet ownership: prevent the legacy two-column minimums from forcing overflow. */
@media(min-width:481px) and (max-width:1024px){
  #menu{max-width:100vw!important}.menu-stage,#play,.daily-run-card,.menu-grid{min-width:0!important}
  .vd4-masthead,.vd6-manual-masthead,.cos-header,.cos-top-tabs,.cos-hero,.cos-loadout-dock,.cos-category-tabs,.cosmetics-gallery,.cos-footer{max-width:100%!important}
}

/* Ultrawide: preserve negative space instead of expanding density indefinitely. */
@media(min-width:2400px){
  #menu{grid-template-columns:520px 760px!important;column-gap:84px!important;justify-content:center!important}
  #menu>.menu-topbar,.menu-grid{max-width:1364px!important}
  .overlay>*{max-width:1240px}
  .result-shell{max-width:1180px!important}
}

@media(hover:none){
  .primary:hover,.secondary:hover,.menu-tile:hover,.daily-run-card:hover,.cos-card:hover,.mastery-card:hover{transform:none!important;filter:none!important}
}
'''

index = index.replace('\n</style>', vd7_css + '\n</style>', 1)

vd7_js = r'''

// === VD7 THEME + RESPONSIVE CERTIFICATION =================================
const VD7_CERT_VERSION='VD7.0.0';
const VD7_THEME_ORDER=Object.freeze(['paper','carbon','cobalt','kelp','plum','mono']);
const VD7_VIEWPORTS=Object.freeze([
 Object.freeze({name:'PHONE-S',width:360,height:640}),
 Object.freeze({name:'PHONE-M',width:390,height:844}),
 Object.freeze({name:'PHONE-L',width:412,height:915}),
 Object.freeze({name:'TABLET-P',width:768,height:1024}),
 Object.freeze({name:'TABLET-L',width:820,height:1180}),
 Object.freeze({name:'DESKTOP-720',width:1280,height:720}),
 Object.freeze({name:'DESKTOP-900',width:1440,height:900}),
 Object.freeze({name:'DESKTOP-FHD',width:1920,height:1080}),
 Object.freeze({name:'DESKTOP-QHD',width:2560,height:1440}),
 Object.freeze({name:'ULTRAWIDE',width:3440,height:1440})
]);
function vd7ParseColor(value){const t=String(value||'').trim(),h=t.match(/^#([0-9a-f]{6})$/i);if(h){const n=parseInt(h[1],16);return[(n>>16)&255,(n>>8)&255,n&255]}const r=t.match(/^rgba?\(\s*(\d+(?:\.\d+)?)\s*[, ]\s*(\d+(?:\.\d+)?)\s*[, ]\s*(\d+(?:\.\d+)?)/i);return r?r.slice(1,4).map(Number):null}
function vd7Luminance(rgb){if(!rgb)return null;const q=rgb.map(v=>{const c=v/255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4});return.2126*q[0]+.7152*q[1]+.0722*q[2]}
function vd7Contrast(a,b){const x=vd7Luminance(vd7ParseColor(a)),y=vd7Luminance(vd7ParseColor(b));if(x==null||y==null)return null;return(Math.max(x,y)+.05)/(Math.min(x,y)+.05)}
function vd7ThemeMetrics(theme){const root=document.documentElement,previous=root.dataset.vcTheme||'paper';root.dataset.vcTheme=theme;const s=getComputedStyle(root),v=n=>s.getPropertyValue(n).trim(),pairs={background:[v('--vc-bg-ink'),v('--vc-bg')],backgroundMuted:[v('--vc-bg-ink-muted'),v('--vc-bg')],surface:[v('--vc-ink'),v('--vc-surface')],surfaceSecondary:[v('--vc-ink-secondary'),v('--vc-surface')],surfaceMuted:[v('--vc-ink-muted'),v('--vc-surface')],accent:[v('--vc-on-accent'),v('--vc-accent')]},contrast={};for(const [k,[a,b]]of Object.entries(pairs)){const c=vd7Contrast(a,b);contrast[k]=c==null?null:+c.toFixed(2)}root.dataset.vcTheme=previous;return Object.freeze({theme,contrast,pass:Object.values(contrast).every(c=>c==null||c>=4.5)})}
function vd7AuditThemes(){const results=VD7_THEME_ORDER.map(vd7ThemeMetrics);return Object.freeze({version:VD7_CERT_VERSION,results,pass:results.every(x=>x.pass)})}
function vd7ViewportClass(){const w=innerWidth,h=innerHeight;if(w>=2400)return'ultrawide';if(w>=1025)return h<=780?'desktop-short':'desktop';if(w>=481)return'tablet';return'phone'}
function vd7VisibleTouchFailures(){return[...document.querySelectorAll('button:not([disabled]),summary,[role="button"]')].filter(el=>{const cs=getComputedStyle(el),r=el.getBoundingClientRect();if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0||r.width<=0||r.height<=0)return false;return r.width<44||r.height<44}).map(el=>({id:el.id||'',className:el.className||'',width:+el.getBoundingClientRect().width.toFixed(1),height:+el.getBoundingClientRect().height.toFixed(1)})).slice(0,20)}
function vd7SyncThemeMeta(){const meta=document.querySelector('meta[name="theme-color"]');if(!meta)return;const bg=getComputedStyle(document.documentElement).getPropertyValue('--vc-bg').trim();if(bg)meta.setAttribute('content',bg)}
function vd7RuntimeAudit(){const themes=vd7AuditThemes(),root=document.documentElement,meta=document.querySelector('meta[name="theme-color"]')?.content||'',bg=getComputedStyle(root).getPropertyValue('--vc-bg').trim(),touchFailures=vd7VisibleTouchFailures(),horizontalOverflow=root.scrollWidth>innerWidth+1||document.body.scrollWidth>innerWidth+1;return Object.freeze({version:VD7_CERT_VERSION,phase:document.querySelector('meta[name="voidcut-visual-phase"]')?.content||'',theme:root.dataset.vcTheme||'paper',themeSuite:themes.pass,themeColorSynced:meta.toLowerCase()===bg.toLowerCase(),viewport:{width:innerWidth,height:innerHeight,className:vd7ViewportClass()},horizontalOverflow,touchFailures,contracts:{build:RELEASE_VERSION,save:SAVE_SCHEMA,replay:RELEASE_CONTRACT.replay,arena:RELEASE_CONTRACT.arena,director:RELEASE_CONTRACT.director,daily:RELEASE_CONTRACT.daily},pass:themes.pass&&!horizontalOverflow&&touchFailures.length===0&&meta.toLowerCase()===bg.toLowerCase()})}
function vd7Initialize(){vd7SyncThemeMeta();document.addEventListener('voidcut:themechange',()=>requestAnimationFrame(vd7SyncThemeMeta));window.addEventListener('resize',vd7SyncThemeMeta,{passive:true});document.documentElement.dataset.vd7Viewport=vd7ViewportClass()}
Object.defineProperty(window,'VoidcutCertification',{value:Object.freeze({version:VD7_CERT_VERSION,themes:VD7_THEME_ORDER,viewports:VD7_VIEWPORTS,auditThemes:vd7AuditThemes,audit:vd7RuntimeAudit,syncThemeColor:vd7SyncThemeMeta}),enumerable:true,configurable:false,writable:false});
'''

marker = '\n// === V6.0 VISUAL RELEASE ============================================='
if marker not in index:
    raise SystemExit('VD7 JS insertion marker missing')
index = index.replace(marker, vd7_js + marker, 1)

startup = 'rebuildRenderGeometry();viewportState=fitViewport();applyUiProductionPolish();renderToggles();applyAccessibilityClasses();vd6InitUtilityLayer();renderCosmetics();showMenu();refreshInstall();refreshFullscreen();requestAnimationFrame(update);'
startup_new = 'rebuildRenderGeometry();viewportState=fitViewport();applyUiProductionPolish();vd7Initialize();renderToggles();applyAccessibilityClasses();vd6InitUtilityLayer();renderCosmetics();showMenu();refreshInstall();refreshFullscreen();requestAnimationFrame(update);'
if startup not in index:
    raise SystemExit('VD7 startup marker missing')
index = index.replace(startup, startup_new, 1)

CSS.write_text(css, encoding='utf-8')
INDEX.write_text(index, encoding='utf-8')
print('VD7 theme + responsive certification layer applied')
print('index bytes:', len(index.encode('utf-8')))
print('design css bytes:', len(css.encode('utf-8')))
